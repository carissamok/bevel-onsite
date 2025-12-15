'use client';

import { useState } from 'react';
import { Message, ChatState } from '@/types/chat';
import { sendMessage, parseChatState } from '@/lib/client';

export default function Home() {
  const [chatState, setChatState] = useState<ChatState>({
    messages: [],
  });
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [chatId] = useState('default'); // For now, using a default chat ID

  const handleSend = async () => {
    if (!inputText.trim() || isLoading) return;

    const userMessage: Message = {
      text: inputText,
      sender: 'User',
      timestamp: new Date(),
    };

    // Optimistically add user message
    const updatedState: ChatState = {
      messages: [...chatState.messages, userMessage].sort(
        (a, b) => a.timestamp.getTime() - b.timestamp.getTime()
      ),
    };
    setChatState(updatedState);
    setInputText('');
    setIsLoading(true);

    try {
      const response = await sendMessage(chatId, inputText, chatState);
      const parsedState = parseChatState(response);
      // Ensure messages are sorted by timestamp
      parsedState.messages.sort(
        (a, b) => a.timestamp.getTime() - b.timestamp.getTime()
      );
      setChatState(parsedState);
    } catch (error) {
      console.error('Error sending message:', error);
      // Revert optimistic update on error
      setChatState(chatState);
      alert('Failed to send message. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleClearChat = () => {
    if (window.confirm('Are you sure you want to clear the chat?')) {
      setChatState({ messages: [] });
      setInputText('');
    }
  };

  const formatTimestamp = (timestamp: Date) => {
    return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-50">
      {/* Sidebar */}
      <aside className="w-80 bg-white dark:bg-white border-r border-gray-200 dark:border-gray-200">
        {/* Sidebar content - empty for now */}
      </aside>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white dark:bg-white border-b border-gray-200 dark:border-gray-200 px-6 py-4">
          <h1 className="text-2xl font-semibold text-gray-900 dark:text-gray-900">Chat with Coach</h1>
        </header>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          <div className="max-w-3xl mx-auto space-y-4">
          {chatState.messages.length === 0 ? (
            <div className="text-center text-gray-500 dark:text-gray-500 mt-12">
              <p className="text-lg">Start a conversation with your coach</p>
              <p className="text-sm mt-2">Type a message below to get started</p>
            </div>
          ) : (
            [...chatState.messages]
              .sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime())
              .map((message, index) => (
              <div
                key={index}
                className={`flex ${
                  message.sender === 'User' ? 'justify-end' : 'justify-start'
                }`}
              >
                <div
                  className={`max-w-[70%] rounded-lg px-4 py-2 ${
                    message.sender === 'User'
                      ? 'bg-blue-500 text-white dark:bg-blue-500 dark:text-white'
                      : 'bg-white dark:bg-white text-gray-900 dark:text-gray-900 border border-gray-200 dark:border-gray-200'
                  }`}
                >
                  <div className="text-sm font-medium mb-1">
                    {message.sender}
                  </div>
                  <div className="text-sm whitespace-pre-wrap break-words">
                    {message.text}
                  </div>
                  <div
                    className={`text-xs mt-1 ${
                      message.sender === 'User'
                        ? 'text-blue-100 dark:text-blue-100'
                        : 'text-gray-500 dark:text-gray-500'
                    }`}
                  >
                    {formatTimestamp(message.timestamp)}
                  </div>
                </div>
              </div>
            ))
          )}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white dark:bg-white border border-gray-200 dark:border-gray-200 rounded-lg px-4 py-2">
                  <div className="text-sm text-gray-500 dark:text-gray-500">Coach is typing...</div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Input Area */}
        <div className="bg-white dark:bg-white border-t border-gray-200 dark:border-gray-200 px-6 py-4">
          <div className="max-w-3xl mx-auto">
            <div className="flex gap-3">
              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message..."
                disabled={isLoading}
                rows={2}
                className="flex-1 resize-none rounded-lg border border-gray-300 dark:border-gray-300 px-4 py-2 text-sm text-gray-900 dark:text-gray-900 bg-white dark:bg-white focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-20 disabled:bg-gray-100 dark:disabled:bg-gray-100 disabled:cursor-not-allowed"
              />
              <button
                onClick={handleSend}
                disabled={!inputText.trim() || isLoading}
                className="px-6 py-2 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                Send
              </button>
              <button
                onClick={handleClearChat}
                disabled={isLoading || chatState.messages.length === 0}
                className="px-4 py-2 bg-gray-200 dark:bg-gray-200 text-gray-700 dark:text-gray-700 rounded-lg font-medium hover:bg-gray-300 dark:hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 disabled:bg-gray-100 dark:disabled:bg-gray-100 disabled:cursor-not-allowed disabled:text-gray-400 dark:disabled:text-gray-400 transition-colors"
                title="Clear chat"
              >
                Clear
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
