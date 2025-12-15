from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Literal
from datetime import datetime
from openai import OpenAI

import json
import os
from dotenv import load_dotenv

from .checkin import save_checkin, update_checkin
from .db import get_active_checkins
from .prompts import create_checkin_system_prompt, update_delete_system_prompt

load_dotenv()

router = APIRouter()

# Initialize OpenAI client lazily
def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    return OpenAI(api_key=api_key)


class ChatMessage(BaseModel):
    text: str
    sender: Literal["User", "Coach"]
    timestamp: str


class Conversation(BaseModel):
    messages: List[ChatMessage]


class SendMessageRequest(BaseModel):
    message: str
    conversation: Conversation


class SendMessageResponse(BaseModel):
    message: ChatMessage
    conversation: Conversation


@router.post("/api/chat/{chat_id}/send", response_model=SendMessageResponse)
async def handle_send_message(chat_id: str, request: SendMessageRequest):
    try:
        if not request.message or not isinstance(request.message, str):
            raise HTTPException(status_code=400, detail="Message is required")

        # Format messages for OpenAI API
        # OpenAI expects messages in format: { role: 'user' | 'assistant', content: string }
        ai_messages = []
        for msg in request.conversation.messages:
            role = "user" if msg.sender == "User" else "assistant"
            ai_messages.append({
                "role": role,
                "content": msg.text
            })

        # Add the current user message
        current_message = {
            "role": "user",
            "content": request.message
        }
        ai_messages.append(current_message)

        # Generate AI response using OpenAI SDK
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=ai_messages
        )

        # check if updating or deleting event
        if not await updateOrDelete(current_message, client):
            await handle_structured_output(current_message, client)

        ai_response = response.choices[0].message.content

        coach_message = handle_conversation(ai_response)

        # Build the updated conversation
        updated_messages = list(request.conversation.messages)
        updated_messages.append(
            ChatMessage(
                text=request.message,
                sender="User",
                timestamp=datetime.now().isoformat()
            )
        )
        updated_messages.append(coach_message)

        # Return response in expected format
        return SendMessageResponse(
            message=coach_message,
            conversation=Conversation(messages=updated_messages)
        )

    except Exception as error:
        print(f"Error handling chat message: {error}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process chat message: {str(error)}"
        )



def handle_conversation(ai_response: str):
    # Create the coach's response message
    coach_message = ChatMessage(
        text=ai_response,
        sender="Coach",
        timestamp=datetime.now().isoformat()
    )
    return coach_message



async def handle_structured_output(user_message, client):

    historical_checkins = get_active_checkins()
    historical_checkins_message = {
        "role": "user",
        "content": (
            "Here are the user's existing active check-ins:\n"
            f"{json.dumps(historical_checkins, indent=2)}")  
    }
    
    messages = [create_checkin_system_prompt, historical_checkins_message, user_message]

    response = client.chat.completions.create(
        model="gpt-5.2",
        messages=messages,
        functions=[{
            "name": "schedule_checkin",
            "description": "Create scheduled check-ins for the user if applicable",
            "parameters": {
                "type": "object",  # must be "object"
                "properties": {
                    "checkins": {      # a property holding the list
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "category": {"type": "string"},
                                "check_in_time": {"type": "string", "format": "date-time"},
                                "message_content": {"type": "string"}
                            },
                            "required": ["category", "check_in_time", "message_content"]
                        }
                    }
                },
                "required": ["checkins"]
            }
        }],
        function_call="auto",  # model decides whether to call it
        max_completion_tokens=250
    )

    # Only save a check-in if the function call is present
    if response.choices[0].message.function_call is not None:
        print("Function call detected, saving check-in...")
        structured_checkin = response.choices[0].message.function_call.arguments
        print("Structured check-in:", structured_checkin)
        if isinstance(structured_checkin, str):
            try:
                structured_checkin_json = json.loads(structured_checkin)
                checkin_list = structured_checkin_json.get("checkins", [])
                for checkin in checkin_list:
                    await save_checkin(checkin)
            except json.JSONDecodeError:
                print("Invalid json response from llm")            

async def updateOrDelete(user_message, client):
    historical_checkins = get_active_checkins()
    historical_checkins_message = {
        "role": "user",
        "content": (
            "Here are the user's existing active check-ins:\n"
            f"{json.dumps(historical_checkins, indent=2)}")  
    }

    messages = [update_delete_system_prompt, historical_checkins_message, user_message]

    response = client.chat.completions.create(
        model="gpt-5.2",
        messages=messages,
        functions=[{
            "name": "update_or_delete_checkin",
            "description": "Update or delete a check-in for the user if applicable",
            "parameters": {
                "type": "object",
                "properties": {
                    "event_ids": {
                        "type": ["array", "null"],
                        "items": { "type": "string" }
                    },
                    "action": {"type": "string", "enum": ["update", "delete", "none"]},
                    "updated_time": {"type": "string", "format": "date-time"},
                    "updated_message": {"type": "string"}
                },
                "required": ["action", "event_ids"]
            }
        }],
        function_call={"name": "update_or_delete_checkin"},
        max_completion_tokens=250
    )

    if response.choices[0].message.function_call is not None:
        print("Checking if updating or deleting check-in...")
        checkin = response.choices[0].message.function_call.arguments

        if isinstance(checkin, str):
            try:
                print("Update/Delete checkin:", checkin)
                checkin_json = json.loads(checkin)
            except json.JSONDecodeError:
                print("Invalid json response from llm")
                return False
            if checkin_json["action"] in ["update", "delete"]:
                update_checkin(checkin_json["event_ids"], checkin_json["action"], 
                    checkin_json.get("updated_time"), checkin_json.get("updated_message"))
                return True
            return False

    return False