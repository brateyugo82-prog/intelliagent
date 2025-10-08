import { NextResponse } from "next/server";

export async function GET(req) {
  const { searchParams } = new URL(req.url);
  const mode = searchParams.get("hub.mode");
  const token = searchParams.get("hub.verify_token");
  const challenge = searchParams.get("hub.challenge");

  if (mode === "subscribe" && token === process.env.META_VERIFY_TOKEN) {
    console.log("✅ Webhook Verification OK");
    return new NextResponse(challenge, { status: 200 });
  }

  console.log("❌ Webhook Verification FAILED");
  return new NextResponse("Verification failed", { status: 403 });
}

export async function POST(req) {
  try {
    const body = await req.json();
    console.log("📩 Meta Event:", body);
  } catch (e) {
    console.error("❌ POST Error:", e);
  }

  return new NextResponse("ok", { status: 200 });
}
