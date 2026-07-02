"use client";

import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { MessageBubble, TypingBubble } from "./message-bubble";

type Message = {
  role: "user" | "assistant";
  content: string;
};

const PLACEHOLDER: Record<"tr" | "en", string> = {
  tr: "Mesajınızı yazın...",
  en: "Type your message...",
};

const DISCLAIMER: Record<"tr" | "en", string> = {
  tr: "Bu asistan genel bilgilendirme amaçlıdır; tıbbi teşhis veya tedavi yerine geçmez.",
  en: "This assistant is for general information only; it does not replace medical diagnosis or treatment.",
};

export function ChatWindow({
  language,
  messages,
  onSend,
  isSending,
}: {
  language: "tr" | "en";
  messages: Message[];
  onSend: (content: string) => void;
  isSending: boolean;
}) {
  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, isSending]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || isSending) return;
    onSend(trimmed);
    setInput("");
  }

  return (
    <div className="flex h-full flex-col">
      <div ref={scrollRef} className="flex-1 space-y-3 overflow-y-auto px-4 py-4">
        {messages.map((message, i) => (
          <MessageBubble key={i} message={message} />
        ))}
        {isSending && <TypingBubble />}
      </div>

      <form onSubmit={handleSubmit} className="border-t border-slate-200 p-3">
        <div className="flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={PLACEHOLDER[language]}
            disabled={isSending}
            className="flex-1 rounded-full border border-slate-200 px-4 py-2 text-sm outline-none focus:border-teal-500 disabled:opacity-50"
          />
          <Button
            type="submit"
            disabled={isSending || !input.trim()}
            className="rounded-full bg-teal-600 text-white hover:bg-teal-700"
          >
            {language === "tr" ? "Gönder" : "Send"}
          </Button>
        </div>
        <p className="mt-2 text-center text-[11px] text-slate-400">{DISCLAIMER[language]}</p>
      </form>
    </div>
  );
}
