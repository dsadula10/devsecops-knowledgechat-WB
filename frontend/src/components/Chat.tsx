import React, { useState, useRef, useEffect } from 'react';
import { MessageBubble, type Message } from './Message';
import { ScrollArea } from './ui/scroll-area';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { Send, Loader2 } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId] = useState(() => crypto.randomUUID());
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    // Create assistant message placeholder
    const assistantMessageId = crypto.randomUUID();
    const assistantMessage: Message = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      toolCalls: [],
    };

    setMessages(prev => [...prev, assistantMessage]);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage.content,
          conversation_id: conversationId,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No response reader');
      }

      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              setMessages(prev => prev.map(msg => {
                if (msg.id !== assistantMessageId) return msg;

                if (data.type === 'token') {
                  return {
                    ...msg,
                    content: msg.content + (data.content || ''),
                  };
                }

                if (data.type === 'tool_call') {
                  return {
                    ...msg,
                    toolCalls: [
                      ...(msg.toolCalls || []),
                      {
                        tool: data.tool,
                        args: data.args,
                        status: 'pending' as const,
                      },
                    ],
                  };
                }

                if (data.type === 'tool_result') {
                  return {
                    ...msg,
                    toolCalls: (msg.toolCalls || []).map(tc =>
                      tc.tool === data.tool && tc.status === 'pending'
                        ? { ...tc, result: data.result, status: 'success' as const }
                        : tc
                    ),
                  };
                }

                if (data.type === 'error') {
                  return {
                    ...msg,
                    content: msg.content + `\n\n❌ Error: ${data.content}`,
                    toolCalls: (msg.toolCalls || []).map(tc =>
                      tc.status === 'pending'
                        ? { ...tc, status: 'error' as const }
                        : tc
                    ),
                  };
                }

                return msg;
              }));
            } catch (e) {
              console.error('Error parsing SSE data:', e);
            }
          }
        }
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => prev.map(msg =>
        msg.id === assistantMessageId
          ? { ...msg, content: '❌ Failed to send message. Please try again.' }
          : msg
      ));
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Header */}
      <div className="border-b border-border bg-card px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="text-3xl">🔐</div>
          <div>
            <h1 className="text-2xl font-bold">DevSecOps Knowledge Chat</h1>
            <p className="text-sm text-muted-foreground">
              AI-powered security assistant with RAG, scanning, and ticket management
            </p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 p-6" ref={scrollAreaRef}>
        <div className="max-w-4xl mx-auto">
          {messages.length === 0 && (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🤖</div>
              <h2 className="text-2xl font-semibold mb-2">Welcome to DevSecOps Chat</h2>
              <p className="text-muted-foreground mb-6">
                Ask me about security policies, vulnerability scans, or create tickets
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-3xl mx-auto">
                <button
                  onClick={() => setInput("What does our password policy say?")}
                  className="p-4 bg-card border border-border rounded-lg hover:bg-accent transition-colors text-left"
                >
                  <div className="text-2xl mb-2">📚</div>
                  <div className="font-medium text-sm">Password Policy</div>
                  <div className="text-xs text-muted-foreground">
                    Search security policies
                  </div>
                </button>
                <button
                  onClick={() => setInput("Show me the latest scan for web-app-1")}
                  className="p-4 bg-card border border-border rounded-lg hover:bg-accent transition-colors text-left"
                >
                  <div className="text-2xl mb-2">🔍</div>
                  <div className="font-medium text-sm">Scan Results</div>
                  <div className="text-xs text-muted-foreground">
                    Check vulnerabilities
                  </div>
                </button>
                <button
                  onClick={() => setInput("Create a ticket for the SQL injection in web-app-1")}
                  className="p-4 bg-card border border-border rounded-lg hover:bg-accent transition-colors text-left"
                >
                  <div className="text-2xl mb-2">🎫</div>
                  <div className="font-medium text-sm">Create Ticket</div>
                  <div className="text-xs text-muted-foreground">
                    File security issues
                  </div>
                </button>
              </div>
            </div>
          )}

          {messages.map(message => (
            <MessageBubble key={message.id} message={message} />
          ))}

          {isLoading && messages[messages.length - 1]?.role === 'assistant' && !messages[messages.length - 1]?.content && (
            <div className="flex gap-3 mb-4">
              <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center">
                🤖
              </div>
              <div className="bg-card border border-border rounded-lg p-4">
                <div className="flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span className="text-sm text-muted-foreground">Thinking...</span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      {/* Input */}
      <div className="border-t border-border bg-card p-4">
        <div className="max-w-4xl mx-auto flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about security policies, scans, or create tickets..."
            disabled={isLoading}
            className="flex-1"
          />
          <Button
            onClick={handleSendMessage}
            disabled={!input.trim() || isLoading}
            size="icon"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </Button>
        </div>
      </div>
    </div>
  );
};
