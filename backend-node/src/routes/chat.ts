import { Request, Response } from 'express';
import { openai } from '@ai-sdk/openai';
import { generateText } from 'ai';

interface ChatMessage {
  text: string;
  sender: 'User' | 'Coach';
  timestamp: string;
}

interface SendMessageRequest {
  message: string;
  conversation: {
    messages: ChatMessage[];
  };
}

interface SendMessageResponse {
  message: {
    text: string;
    sender: 'User' | 'Coach';
    timestamp: string;
  };
  conversation: {
    messages: ChatMessage[];
  };
}

export async function handleSendMessage(req: Request, res: Response) {
  try {
    const { id: chatId } = req.params;
    const { message, conversation }: SendMessageRequest = req.body;

    if (!message || typeof message !== 'string') {
      return res.status(400).json({ error: 'Message is required' });
    }

    // Format messages for AI SDK
    // The AI SDK expects messages in format: { role: 'user' | 'assistant', content: string }
    const aiMessages = conversation.messages.map((msg) => ({
      role: msg.sender === 'User' ? ('user' as const) : ('assistant' as const),
      content: msg.text,
    }));

    // Add the current user message
    aiMessages.push({
      role: 'user' as const,
      content: message,
    });

    // Generate AI response using Vercel AI SDK
    const { text: aiResponse } = await generateText({
      model: openai('gpt-3.5-turbo'),
      messages: aiMessages,
    });

    // Create the coach's response message
    const coachMessage: ChatMessage = {
      text: aiResponse,
      sender: 'Coach',
      timestamp: new Date().toISOString(),
    };

    // Build the updated conversation
    const updatedMessages: ChatMessage[] = [
      ...conversation.messages,
      {
        text: message,
        sender: 'User',
        timestamp: new Date().toISOString(),
      },
      coachMessage,
    ];

    // Return response in expected format
    const response: SendMessageResponse = {
      message: coachMessage,
      conversation: {
        messages: updatedMessages,
      },
    };

    res.json(response);
  } catch (error) {
    console.error('Error handling chat message:', error);
    res.status(500).json({ 
      error: 'Failed to process chat message',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
}

