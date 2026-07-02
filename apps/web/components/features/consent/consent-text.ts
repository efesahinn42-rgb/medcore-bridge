export const CONSENT_TEXT: Record<"tr" | "en", { title: string; body: string; accept: string; decline: string }> = {
  tr: {
    title: "Devam etmeden önce",
    body: "Bu sohbet, sorularınızı yanıtlamak için yapay zeka kullanır ve KVKK/GDPR kapsamında kişisel verilerinizi (isim, telefon gibi) işleyebilir. Mesajlarınızdaki kişisel bilgiler yapay zekaya iletilmeden önce yerel olarak maskelenir. Bu asistan tıbbi teşhis veya tedavi önermez, yalnızca genel bilgilendirme amaçlıdır. Devam ederek bu koşulları kabul etmiş olursunuz.",
    accept: "Kabul Ediyorum, Devam Et",
    decline: "Kabul Etmiyorum",
  },
  en: {
    title: "Before we continue",
    body: "This chat uses AI to answer your questions and may process personal data (such as your name or phone number) under KVKK/GDPR. Personal information in your messages is masked locally before it ever reaches the AI. This assistant does not provide medical diagnosis or treatment — it is for general information only. By continuing, you agree to these terms.",
    accept: "I Agree, Continue",
    decline: "I Do Not Agree",
  },
};
