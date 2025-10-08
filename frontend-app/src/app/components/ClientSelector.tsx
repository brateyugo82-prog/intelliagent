"use client";
import React from "react";

type Props = { onSelect: (value: string) => void };

export default function ClientSelector({ onSelect }: Props) {
  const clients = [
    { value: "mtm", label: "MTM – Möbel Transport Montage" }
  ];

  return (
    <select
      onChange={(e) => onSelect(e.target.value)}
      style={{ padding: "0.5rem", marginBottom: "1rem", width: "100%" }}
    >
      <option value="">-- Bitte Kunde wählen --</option>
      {clients.map((c) => (
        <option key={c.value} value={c.value}>
          {c.label}
        </option>
      ))}
    </select>
  );
}
