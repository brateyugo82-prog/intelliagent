// ✅ /frontend-app/app/api/meta/webhook/route.js
import { NextResponse } from "next/server";

const VERIFY_TOKEN = "intelliagent_webhook"; // Muss exakt mit Meta übereinstimmen

// GET: Wird von Meta zum Verifizieren aufgerufen
export async function GET(req) {
  const { searchParams } = new URL(req.url);
  const mode = searchParams.get("hub.mode");
  const token = searchParams.get("hub.verify_token");
  const challenge = searchParams.get("hub.challenge");

  if (mode === "subscribe" && token === VERIFY_TOKEN) {
    console.log("✅ Webhook bestätigt von Meta");
    return new NextResponse(challenge, { status: 200 });
  }

  console.warn("❌ Ungültige Anfrage:", { mode, token });
  return new NextResponse("Verification failed", { status: 403 });
}

// POST: Wenn Meta Events sendet (Kommentare, Nachrichten, etc.)
export async function POST(req) {
  try {
    const body = await req.json();
    console.log("📬 Meta Event empfangen:", JSON.stringify(body, null, 2));
    return NextResponse.json({ received: true });
  } catch (err) {
    console.error("❌ Fehler beim Empfangen:", err);
    return NextResponse.json({ error: "Invalid body" }, { status: 400 });
  }
}
