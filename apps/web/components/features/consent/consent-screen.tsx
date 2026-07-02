"use client";

import { Button } from "@/components/ui/button";
import { CONSENT_TEXT } from "./consent-text";

type Language = "tr" | "en";

export function ConsentScreen({
  language,
  onLanguageChange,
  onDecide,
  isSubmitting,
}: {
  language: Language;
  onLanguageChange: (language: Language) => void;
  onDecide: (consentGiven: boolean) => void;
  isSubmitting: boolean;
}) {
  const text = CONSENT_TEXT[language];

  return (
    <div className="flex h-full flex-col items-center justify-center gap-6 p-8 text-center">
      <div className="flex gap-2">
        {(["tr", "en"] as const).map((lang) => (
          <button
            key={lang}
            onClick={() => onLanguageChange(lang)}
            className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
              language === lang
                ? "bg-teal-600 text-white"
                : "bg-slate-100 text-slate-500 hover:bg-slate-200"
            }`}
          >
            {lang.toUpperCase()}
          </button>
        ))}
      </div>

      <div className="max-w-sm space-y-3">
        <h2 className="text-lg font-semibold text-slate-900">{text.title}</h2>
        <p className="text-sm leading-relaxed text-slate-600">{text.body}</p>
      </div>

      <div className="flex w-full max-w-sm flex-col gap-2">
        <Button
          onClick={() => onDecide(true)}
          disabled={isSubmitting}
          className="bg-teal-600 text-white hover:bg-teal-700"
        >
          {text.accept}
        </Button>
        <Button
          onClick={() => onDecide(false)}
          disabled={isSubmitting}
          variant="ghost"
          className="text-slate-500"
        >
          {text.decline}
        </Button>
      </div>
    </div>
  );
}
