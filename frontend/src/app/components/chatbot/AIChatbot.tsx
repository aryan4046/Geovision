import { useState, useEffect, useRef } from "react";
import { MessageCircle, X, Send, Bot, User, MapPin, TrendingUp, Building2, Sparkles } from "lucide-react";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { ScrollArea } from "../ui/scroll-area";
import type { LocationData } from "../dashboard/Dashboard";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
};

type AIChatbotProps = {
  isOpen: boolean;
  onToggle: () => void;
  selectedLocation?: LocationData | null;
  businessType?: string;
};

import { apiService } from "../../../services/apiService";

export function AIChatbot({ isOpen, onToggle, selectedLocation, businessType = "restaurant" }: AIChatbotProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content: "👋 Hi! I'm your **GeoVision AI** assistant powered by advanced geospatial analytics.\n\nI can help you:\n• Find optimal locations for your business across India\n• Analyze site readiness and demographics\n• Compare different areas\n• Provide market insights and recommendations\n\nWhat would you like to know?",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const handleSend = () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsTyping(true);

    apiService.fetchChat(input, { selectedLocation, businessType })
      .then(data => {
        const aiMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: data.reply || data.response || data.message || "I am here to help!",
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, aiMessage]);
      })
      .catch(err => {
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: "Sorry, I am having trouble connecting to the network right now.",
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      })
      .finally(() => setIsTyping(false));
  };

  const handleQuickAction = (action: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: action,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsTyping(true);

    apiService.fetchChat(action, { selectedLocation, businessType })
      .then(data => {
        const aiMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: data.reply || data.response || data.message || "I am here to help!",
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, aiMessage]);
      })
      .catch(err => {
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: "Sorry, I am having trouble connecting to the network right now.",
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      })
      .finally(() => setIsTyping(false));
  };

  const quickActions = [
    { icon: MapPin, label: "Best locations", query: "What are the best locations for my business?" },
    { icon: TrendingUp, label: "Current location", query: "Tell me about the current selected location" },
    { icon: Building2, label: "Compare areas", query: "How do I compare different areas?" },
    { icon: Sparkles, label: "Growth zones", query: "Show me high-growth areas" },
  ];

  if (!isOpen) {
    return (
      <button
        onClick={onToggle}
        className="fixed bottom-8 right-8 w-16 h-16 rounded-full bg-gradient-to-br from-indigo-500 via-purple-600 to-fuchsia-600 text-white shadow-[0_0_30px_rgba(168,85,247,0.6)] z-50 hover:scale-110 transition-transform border border-white/20 flex items-center justify-center group overflow-hidden"
      >
        <div className="absolute inset-0 bg-white/20 opacity-0 group-hover:opacity-100 transition-opacity"></div>
        <Bot className="w-8 h-8 relative z-10 drop-shadow-md" />
        <div className="absolute -top-1 -right-1 flex h-4 w-4">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-pink-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-4 w-4 bg-pink-500 border border-white/50"></span>
        </div>
      </button>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 w-[440px] h-[calc(100vh-140px)] max-h-[450px] bg-[#0f172a] border border-white/20 rounded-2xl shadow-2xl flex flex-col z-50 animate-in slide-in-from-bottom-4 overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-white/10 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center">
            <Bot className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-sm font-medium text-white">GeoVision AI</h3>
            <p className="text-xs text-green-400 flex items-center gap-1">
              <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
              Online
            </p>
          </div>
        </div>
        <Button
          size="icon"
          variant="ghost"
          onClick={onToggle}
          className="text-gray-400 hover:text-white hover:bg-white/10"
        >
          <X className="w-5 h-5" />
        </Button>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 p-4 min-h-0">
        <div className="space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex gap-3 ${message.role === "user" ? "justify-end" : "justify-start"} animate-in fade-in slide-in-from-bottom-2`}
            >
              {message.role === "assistant" && (
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center flex-shrink-0 shadow-lg">
                  <Bot className="w-4 h-4 text-white" />
                </div>
              )}
              <div
                className={`max-w-[75%] rounded-xl p-3 ${
                  message.role === "user"
                    ? "bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-lg"
                    : "bg-white/10 text-gray-200 backdrop-blur-sm"
                }`}
              >
                <p className="text-sm whitespace-pre-line leading-relaxed">{message.content}</p>
                <p className="text-xs opacity-50 mt-1">
                  {message.timestamp.toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </p>
              </div>
              {message.role === "user" && (
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-gray-600 to-gray-700 flex items-center justify-center flex-shrink-0 shadow-lg">
                  <User className="w-4 h-4 text-white" />
                </div>
              )}
            </div>
          ))}
          
          {/* Typing Indicator */}
          {isTyping && (
            <div className="flex gap-3 justify-start animate-in fade-in slide-in-from-bottom-2">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center flex-shrink-0 shadow-lg">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <div className="bg-white/10 backdrop-blur-sm rounded-xl px-4 py-3">
                <div className="flex gap-1.5">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }}></div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      {/* Quick Actions */}
      {messages.length <= 2 && !isTyping && (
        <div className="px-4 pb-2">
          <p className="text-xs text-gray-400 mb-2">Quick actions:</p>
          <div className="grid grid-cols-2 gap-2">
            {quickActions.map((action, idx) => (
              <button
                key={idx}
                onClick={() => handleQuickAction(action.query)}
                className="flex items-center gap-2 p-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/5 hover:border-purple-500/50 text-left text-xs text-gray-300 hover:text-white transition-all group"
              >
                <action.icon className="w-3.5 h-3.5 text-purple-400 group-hover:text-purple-300" />
                <span>{action.label}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="p-4 border-t border-white/10">
        <div className="flex gap-2">
          <Input
            placeholder="Ask me anything..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleSend()}
            className="flex-1 bg-white/5 border-white/10 text-white placeholder:text-gray-400 focus:border-purple-500"
          />
          <Button
            onClick={handleSend}
            disabled={!input.trim()}
            className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white disabled:opacity-50"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
        <p className="text-xs text-gray-500 mt-2 text-center">
          AI-powered location recommendations across India
        </p>
      </div>
    </div>
  );
}