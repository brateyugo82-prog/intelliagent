"use client";
import Image from "next/image";
import React, { useState } from "react";
import ClientSelector from "./components/ClientSelector";
import WorkflowButton from "./components/WorkflowButton";
import Card from "./components/Card";

export default function Home() {
  const [client, setClient] = useState("");
  const [prompt, setPrompt] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const platform = "website";

  return (
    <div className="font-sans min-h-screen flex flex-col items-center justify-between p-8 bg-gray-50 dark:bg-[#181818]">
      <header className="w-full flex flex-col items-center gap-2 mb-8">
        <Image
          src="/favicon.ico"
          alt="IntelliAgent Logo"
          width={48}
          height={48}
        />
        <h1 className="text-2xl font-bold tracking-tight text-center">
          IntelliAgent Multi-Agenten Plattform
        </h1>
      </header>
      <main className="flex flex-col gap-6 items-center w-full max-w-md">
        <ClientSelector onSelect={setClient} />
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Was sollen die Agenten generieren?"
          required
          style={{
            width: "100%",
            minHeight: 100,
            margin: "20px 0",
            padding: 10,
            borderRadius: 8,
            border: "1px solid #ccc",
            fontSize: 16,
          }}
        />
        <WorkflowButton
          client={client}
          prompt={prompt}
          platform={platform}
          setResult={setResult}
          setLoading={setLoading}
        />
        <Card result={result} loading={loading} platform={platform} />
      </main>
      <footer className="w-full text-center text-sm text-gray-500 mt-8">
        Powered by IntelliAgent 🚀
      </footer>
    </div>
  );
}
