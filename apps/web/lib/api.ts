const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type ConsentResponse = {
  user_id: string;
  conversation_id: string | null;
};

export type ChatMessageResponse = {
  role: string;
  content: string;
};

async function postJson<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    throw new Error(`API hatası (${res.status}): ${path}`);
  }
  return res.json() as Promise<T>;
}

export function submitConsent(
  clinicId: string,
  consentGiven: boolean,
  language: string,
): Promise<ConsentResponse> {
  return postJson(`/clinics/${clinicId}/consent`, {
    consent_given: consentGiven,
    language,
  });
}

export function sendMessage(
  conversationId: string,
  content: string,
): Promise<ChatMessageResponse> {
  return postJson(`/conversations/${conversationId}/messages`, { content });
}
