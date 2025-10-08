"use client";
import React from "react";

/**
 * Wichtig: NEXT_PUBLIC_BACKEND_URL muss in .env.local gesetzt sein (z.B. http://127.0.0.1:8000 oder Render-URL).
 * Das Frontend ruft dann IMMER FastAPI auf, nicht das Next.js-eigene API-Routing.
 * Der Workflow-Button darf nie mehr einen 404 auf :3000/api/workflow/start werfen, sondern immer das echte Backend erreichen.
 */

type WorkflowButtonProps = {
  client: string;
  prompt: string;
  platform: string;
  setResult: (result: any) => void;
  setLoading: (loading: boolean) => void;
};

export default function WorkflowButton({ client, prompt, platform, setResult, setLoading }: WorkflowButtonProps) {
  const handleClick = async () => {
    if (!client) return;
    setLoading(true);
    setResult(null);
    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;
      const res = await fetch(`${backendUrl}/api/workflow/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ client, prompt, platform }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        console.error("Workflow-API-Fehler:", err);
        setResult({ error: err.detail || `Fehler: ${res.status}` });
        return;
      }
      const data = await res.json();
      if (process.env.NODE_ENV === "development") {
        console.log("[WorkflowButton] Ergebnis:", data);
      }
      setResult(data);
    } catch (e) {
      setResult({ error: "Fehler beim Starten des Workflows." });
    } finally {
      setLoading(false);
    }
  };
  return (
    <button
      className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:bg-gray-400"
      onClick={handleClick}
      disabled={!client}
    >
      Generieren
    </button>
  );
}
