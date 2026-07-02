"use client";

import { useState } from "react";
import { ConsentScreen } from "@/components/features/consent/consent-screen";
import { sendMessage, submitConsent } from "@/lib/api";
import { ChatWindow } from "./chat-window";

type Language = "tr" | "en";
type Stage = "consent" | "chat" | "declined";
type Message = { role: "user" | "assistant"; content: string };

const DECLINED_TEXT: Record<Language, string> = {
  tr: "Rıza vermediğiniz için sohbeti başlatamıyoruz. Dilediğiniz zaman geri gelip tekrar deneyebilirsiniz.",
  en: "We can't start the chat without your consent. You're welcome to come back anytime.",
};

const WELCOME_TEXT: Record<Language, string> = {
  tr: "Merhaba! Size nasıl yardımcı olabilirim? Fiyatlar, süreç veya klinik hakkında sorularınızı yanıtlayabilirim.",
  en: "Hello! How can I help you? I can answer questions about pricing, procedures, or the clinic.",
};

const ERROR_TEXT: Record<Language, string> = {
  tr: "Bir sorun oluştu, lütfen tekrar deneyin.",
  en: "Something went wrong, please try again.",
};

export function ChatWidget({ clinicId }: { clinicId: string }) {
  const [language, setLanguage] = useState<Language>("tr");
  const [stage, setStage] = useState<Stage>("consent");
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isSubmittingConsent, setIsSubmittingConsent] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleConsentDecision(consentGiven: boolean) {
    setIsSubmittingConsent(true);
    setError(null);
    try {
      const result = await submitConsent(clinicId, consentGiven, language);
      if (result.conversation_id) {
        setConversationId(result.conversation_id);
        setMessages([{ role: "assistant", content: WELCOME_TEXT[language] }]);
        setStage("chat");
      } else {
        setStage("declined");
      }
    } catch {
      setError(ERROR_TEXT[language]);
    } finally {
      setIsSubmittingConsent(false);
    }
  }

  async function handleSend(content: string) {
    if (!conversationId) return;
    setMessages((prev) => [...prev, { role: "user", content }]);
    setIsSending(true);
    setError(null);
    try {
      const response = await sendMessage(conversationId, content);
      setMessages((prev) => [...prev, { role: "assistant", content: response.content }]);
    } catch {
      setError(ERROR_TEXT[language]);
    } finally {
      setIsSending(false);
    }
  }

  return (
    <div className="flex h-[640px] w-full max-w-sm flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl">
      <div className="flex items-center gap-2 bg-teal-600 px-4 py-3 text-white">
        <div className="size-8 rounded-full bg-white/20" />
        <div>
          <p className="text-sm font-semibold">Demo Klinik</p>
          <p className="text-xs text-teal-100">AI Asistan · genellikle hemen yanıtlar</p>
        </div>
      </div>

      <div className="min-h-0 flex-1">
        {stage === "consent" && (
          <ConsentScreen
            language={language}
            onLanguageChange={setLanguage}
            onDecide={handleConsentDecision}
            isSubmitting={isSubmittingConsent}
          />
        )}
        {stage === "declined" && (
          <div className="flex h-full items-center justify-center p-8 text-center text-sm text-slate-500">
            {DECLINED_TEXT[language]}
          </div>
        )}
        {stage === "chat" && (
          <ChatWindow
            language={language}
            messages={messages}
            onSend={handleSend}
            isSending={isSending}
          />
        )}
      </div>

      {error && (
        <p className="border-t border-red-100 bg-red-50 px-4 py-2 text-center text-xs text-red-600">
          {error}
        </p>
      )}
    </div>
  );
}
