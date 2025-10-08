// "use client" ist notwendig, weil Card dynamische Props nutzt
"use client";
import React from "react";

type CardProps = {
  result: any;
  loading: boolean;
  platform: string;
};

// Neue Reihenfolge der Agenten
const agentSections = [
  { key: "content_agent", label: "ContentAgent", desc: "Textvorschlag" },
  { key: "design_agent", label: "DesignAgent", desc: "Designbeschreibung oder Bild" },
  { key: "communication_agent", label: "CommunicationAgent", desc: "Social Media Text / Kundenkommunikation" },
  { key: "publish_agent", label: "PublishAgent", desc: "Veröffentlichungsvorschlag" },
  { key: "analytics_agent", label: "AnalyticsAgent", desc: "Analyse / Empfehlungen" },
];

export default function Card({ result, loading, platform }: CardProps) {
  if (loading) {
    return (
      <div className="border rounded p-4 min-w-[300px] text-center">
        Workflow läuft…
      </div>
    );
  }

  if (!result) {
    return (
      <div className="border rounded p-4 min-w-[300px] text-center text-gray-500">
        Noch kein Workflow gestartet
      </div>
    );
  }

  if (result.error) {
    return (
      <div className="border rounded p-4 min-w-[300px] text-center text-red-600">
        {result.error || "Unbekannter Fehler"}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4 w-full">
      {agentSections.map(({ key, label, desc }) =>
        result.result && result.result[key] ? (
          <div
            key={key}
            className="border rounded-lg shadow bg-white dark:bg-gray-900 p-4"
          >
            <div className="font-bold text-lg mb-1">{label} Ergebnis</div>
            <div className="text-xs text-gray-500 mb-2">
              Plattform: {platform || "-"}
            </div>
            <div className="italic text-xs text-gray-400 mb-2">{desc}</div>

            {/* Spezielles Handling für DesignAgent */}
            {key === "design_agent" &&
            typeof result.result[key].design === "string" &&
            (result.result[key].design.startsWith("http") ||
              result.result[key].design.startsWith("/static/")) ? (
              <div>
                <img
                  src={result.result[key].design}
                  alt="DesignAgent Output"
                  className="rounded border max-w-full mb-2"
                />
                {/* Mode-Anzeige */}
                {result.result[key].mode && (
                  <div className="text-xs text-green-600">
                    Modus: {result.result[key].mode}
                  </div>
                )}
              </div>
            ) : (
              <div className="bg-gray-100 dark:bg-gray-800 rounded px-2 py-1 text-sm whitespace-pre-wrap">
                {typeof result.result[key] === "object"
                  ? JSON.stringify(result.result[key], null, 2)
                  : String(result.result[key])}
              </div>
            )}
          </div>
        ) : null
      )}

      {/* Fallback, falls keine Agenten-Ergebnisse */}
      {result.result &&
        agentSections.every(({ key }) => !result.result[key]) && (
          <div className="text-gray-500">Keine Agenten-Ergebnisse vorhanden.</div>
        )}
    </div>
  );
}
