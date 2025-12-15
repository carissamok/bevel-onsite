from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Literal
from datetime import datetime
from openai import OpenAI
import os
from dotenv import load_dotenv

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
        ai_messages.append({
            "role": "user",
            "content": request.message
        })

        # Generate AI response using OpenAI SDK
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=ai_messages
        )

        ai_response = response.choices[0].message.content

        # Create the coach's response message
        coach_message = ChatMessage(
            text=ai_response,
            sender="Coach",
            timestamp=datetime.now().isoformat()
        )

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

