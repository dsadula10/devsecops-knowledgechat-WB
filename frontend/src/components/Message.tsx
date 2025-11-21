import React from 'react';
import { cn } from '@/lib/utils';
import { ToolCall } from './ToolCall';
import ReactMarkdown from 'react-markdown';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  toolCalls?: Array<{
    tool: string;
    args: Record<string, any>;
    result?: any;
    status: 'pending' | 'success' | 'error';
  }>;
}

interface MessageBubbleProps {
  message: Message;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div className={cn(
      "flex gap-3 mb-4 animate-fade-in",
      isUser ? "justify-end" : "justify-start"
    )}>
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-sm font-semibold flex-shrink-0">
            🤖
        </div>
      )}
      
      <div className={cn(
        "max-w-[80%] rounded-lg p-4",
        isUser 
          ? "bg-primary text-primary-foreground" 
          : "bg-card border border-border"
      )}>
        {/* Tool calls */}
        {!isUser && message.toolCalls && message.toolCalls.length > 0 && (
          <div className="mb-3">
            {message.toolCalls.map((toolCall, idx) => (
              <ToolCall
                key={idx}
                tool={toolCall.tool}
                args={toolCall.args}
                result={toolCall.result}
                status={toolCall.status}
              />
            ))}
          </div>
        )}

        {/* Message content */}
        <div className={cn(
          "text-sm prose prose-sm dark:prose-invert max-w-none",
          isUser && "prose-invert"
        )}>
          {isUser ? (
            <p className="m-0">{message.content}</p>
          ) : (
            <ReactMarkdown>{message.content}</ReactMarkdown>
          )}
        </div>

        {/* Timestamp */}
        <div className={cn(
          "text-xs mt-2 opacity-60",
          isUser ? "text-right" : "text-left"
        )}>
          {message.timestamp.toLocaleTimeString()}
        </div>
      </div>

      {isUser && (
        <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center text-sm font-semibold flex-shrink-0">
          👤
        </div>
      )}
    </div>
  );
};
