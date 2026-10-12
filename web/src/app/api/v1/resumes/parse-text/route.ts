import { NextRequest, NextResponse } from "next/server";
import { parseFullResume } from "@/lib/server-engine";

export async function POST(req: NextRequest) {
  try {
    const backendUrl = process.env.BACKEND_URL;
    if (backendUrl) {
      try {
        const body = await req.json();
        const res = await fetch(`${backendUrl}/api/v1/resumes/parse-text`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: req.headers.get("Authorization") || "Bearer demo-token",
          },
          body: JSON.stringify(body),
        });
        if (res.ok) {
          return NextResponse.json(await res.json());
        }
      } catch (e) {
        console.warn("Backend forward failed, processing with native engine:", e);
      }
    }

    const { text } = await req.json();
    const parsed = parseFullResume(text || "");

    return NextResponse.json(parsed);
  } catch (error: any) {
    return NextResponse.json({ detail: error?.message || "Parsing failed" }, { status: 500 });
  }
}
