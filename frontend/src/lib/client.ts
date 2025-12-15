import { Message, ChatState } from '@/types/chat';

interface SendMessageRequest {
  message: string;
  conversation: {
    messages: Array<{
      text: string;
      sender: 'User' | 'Coach';
      timestamp: string; // Serialized as ISO string for JSON
    }>;
  };
}

interface SendMessageResponse {
  message: {
    text: string;
    sender: 'User' | 'Coach';
    timestamp: string; // ISO string from backend
  };
  conversation: {
    messages: Array<{
      text: string;
      sender: 'User' | 'Coach';
      timestamp: string; // ISO string from backend
    }>;
  };
}

export async function sendMessage(
  chatId: string,
  newMessage: string,
  currentConversation: ChatState
): Promise<SendMessageResponse> {
  // Serialize Date objects to ISO strings for JSON
  const requestBody: SendMessageRequest = {
    message: newMessage,
    conversation: {
      messages: currentConversation.messages.map((msg) => ({
        text: msg.text,
        sender: msg.sender,
        timestamp: msg.timestamp.toISOString(),
      })),
    },
  };

  // Use environment variable for API URL, fallback to localhost:3001 (Express backend)
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';
  const response = await fetch(`${apiUrl}/api/chat/${chatId}/send`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(requestBody),
  });

  if (!response.ok) {
    throw new Error(`Failed to send message: ${response.statusText}`);
  }

  return response.json();
}

// Helper function to convert API response to ChatState with Date objects
export function parseChatState(response: SendMessageResponse): ChatState {
  return {
    messages: response.conversation.messages.map((msg) => ({
      text: msg.text,
      sender: msg.sender,
      timestamp: new Date(msg.timestamp),
    })),
  };
}

