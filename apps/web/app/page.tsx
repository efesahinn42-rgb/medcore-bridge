import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 p-8">
      <h1 className="text-2xl font-semibold">MedCoreBridge</h1>
      <div className="flex gap-4">
        <Link className="underline" href="/widget">
          Widget
        </Link>
        <Link className="underline" href="/dashboard">
          Klinik Paneli
        </Link>
      </div>
    </main>
  );
}
