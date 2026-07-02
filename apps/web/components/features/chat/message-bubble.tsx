type Message = {
  role: "user" | "assistant";
  content: string;
};

export function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed whitespace-pre-wrap ${
          isUser
            ? "rounded-br-sm bg-teal-600 text-white"
            : "rounded-bl-sm bg-slate-100 text-slate-800"
        }`}
      >
        {message.content}
      </div>
    </div>
  );
}

export function TypingBubble() {
  return (
    <div className="flex justify-start">
      <div className="flex items-center gap-1 rounded-2xl rounded-bl-sm bg-slate-100 px-4 py-3">
        {[0, 1, 2].map((i) => (
          <span
            key={i}
            className="size-1.5 animate-bounce rounded-full bg-slate-400"
            style={{ animationDelay: `${i * 120}ms` }}
          />
        ))}
      </div>
    </div>
  );
}
