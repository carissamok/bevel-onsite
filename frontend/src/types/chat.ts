export type MessageSender = 'User' | 'Coach';

export interface Message {
  text: string;
  sender: MessageSender;
  timestamp: Date;
}

export interface ChatState {
  messages: Message[];
}

