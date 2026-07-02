import { ChatWidget } from "@/components/features/chat/chat-widget";

const DEMO_CLINIC_ID =
  process.env.NEXT_PUBLIC_DEMO_CLINIC_ID ?? "361e231e-f415-45a7-a2c6-2780f53f043d";

export default function WidgetPage() {
  return (
    <main className="min-h-screen bg-slate-50">
      {/* Widget'ın gerçekte bir klinik web sitesine gömüldüğünü göstermek için sahte bir sayfa */}
      <div className="mx-auto max-w-3xl px-6 py-16">
        <p className="text-sm font-medium text-teal-600">Demo Klinik</p>
        <h1 className="mt-2 text-3xl font-semibold text-slate-900">
          Saç Ekimi &amp; Diş Estetiği Merkezi
        </h1>
        <p className="mt-4 max-w-xl text-slate-600">
          Bu, MedCoreBridge sohbet widget&apos;ının bir klinik web sitesine nasıl
          göründüğünü gösteren bir demo sayfasıdır. Sağ alttaki sohbet kutusunu
          kullanarak hasta deneyimini test edebilirsiniz.
        </p>
      </div>

      <div className="fixed right-6 bottom-6 z-50">
        <ChatWidget clinicId={DEMO_CLINIC_ID} />
      </div>
    </main>
  );
}
