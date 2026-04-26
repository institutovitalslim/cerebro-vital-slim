"use client";

import { useState, useRef, useEffect } from "react";
import { Button, Card, Container, Input } from "@/components/ui";
import { SessionGuard } from "@/components/session-guard";

interface Message {
  id: number;
  sender: "me" | "them";
  text: string;
  time: string;
}

const initialMessages: Message[] = [
  {
    id: 1,
    sender: "them",
    text: "Olá! Vi que você tem interesse na Aurora Park Residence. Posso agendar uma visita para você?",
    time: "10:30",
  },
  {
    id: 2,
    sender: "me",
    text: "Olá! Sim, gostaria muito de conhecer o imóvel. Quais são os horários disponíveis?",
    time: "10:32",
  },
  {
    id: 3,
    sender: "them",
    text: "Temos vagas na próxima segunda-feira à tarde (14h-18h) ou sábado pela manhã. Qual prefere?",
    time: "10:35",
  },
];

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = () => {
    if (!input.trim()) return;
    const newMsg: Message = {
      id: messages.length + 1,
      sender: "me",
      text: input.trim(),
      time: new Date().toLocaleTimeString("pt-BR", {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };
    setMessages((m) => [...m, newMsg]);
    setInput("");

    // Mock reply
    setTimeout(() => {
      const reply: Message = {
        id: messages.length + 2,
        sender: "them",
        text: "Perfeito! Vou verificar a disponibilidade e retorno em breve.",
        time: new Date().toLocaleTimeString("pt-BR", {
          hour: "2-digit",
          minute: "2-digit",
        }),
      };
      setMessages((m) => [...m, reply]);
    }, 1200);
  };

  return (
    <SessionGuard>
      <div className="min-h-screen bg-slate-50 flex flex-col">
        <div className="bg-white border-b border-slate-100 py-4">
          <Container>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-brand-100 flex items-center justify-center text-brand-700 font-semibold text-sm">
                CM
              </div>
              <div>
                <h1 className="font-medium text-slate-900 text-sm">
                  Corretor Match
                </h1>
                <p className="text-xs text-slate-400">Online</p>
              </div>
            </div>
          </Container>
        </div>

        <Container className="flex-1 py-6 max-w-2xl">
          <div className="space-y-4">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${
                  msg.sender === "me" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-[80%] px-4 py-3 rounded-2xl text-sm ${
                    msg.sender === "me"
                      ? "bg-brand-700 text-white rounded-br-md"
                      : "bg-white text-slate-700 border border-slate-100 rounded-bl-md"
                  }`}
                >
                  <p>{msg.text}</p>
                  <span
                    className={`text-xs mt-1 block ${
                      msg.sender === "me"
                        ? "text-brand-200"
                        : "text-slate-400"
                    }`}
                  >
                    {msg.time}
                  </span>
                </div>
              </div>
            ))}
            <div ref={bottomRef} />
          </div>
        </Container>

        <div className="bg-white border-t border-slate-100 py-4">
          <Container className="max-w-2xl">
            <div className="flex gap-2">
              <Input
                placeholder="Digite sua mensagem..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && send()}
                className="flex-1"
              />
              <Button onClick={send}>Enviar</Button>
            </div>
          </Container>
        </div>
      </div>
    </SessionGuard>
  );
}
