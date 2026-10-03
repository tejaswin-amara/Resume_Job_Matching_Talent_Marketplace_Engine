import { NextRequest, NextResponse } from "next/server";

const KNOWN_SKILLS = [
  "Python", "TypeScript", "JavaScript", "React", "Next.js", "Node.js",
  "SQL", "PostgreSQL", "Docker", "Kubernetes", "AWS", "FastAPI",
  "Machine Learning", "Git", "Algorithms", "Data Structures",
  "Tailwind CSS", "GraphQL", "Java", "C++", "Go", "Rust", "CI/CD", "Linux"
];

export async function POST(req: NextRequest) {
  try {
    const { text } = await req.json();
    const lower = (text || "").toLowerCase();
    const matched = KNOWN_SKILLS.filter(s => lower.includes(s.toLowerCase()));

    return NextResponse.json({
      skills: matched.length > 0 ? matched : ["TypeScript", "React", "Git"],
      experience: [],
      education: [],
      rawText: text || ""
    });
  } catch (error: any) {
    return NextResponse.json({ error: error.message || "Failed to parse text" }, { status: 500 });
  }
}
