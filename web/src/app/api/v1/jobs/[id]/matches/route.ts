import { NextRequest, NextResponse } from "next/server";
import { INITIAL_JOBS, calculateHybridATSScore } from "@/lib/server-engine";

const SAMPLE_CANDIDATES = [
  {
    name: "Alex Mercer",
    skills: ["Python", "FastAPI", "TypeScript", "React", "PostgreSQL", "Docker"],
    years_experience: 6.5,
    education_level: 4,
    raw_text: "Senior Full-Stack Engineer with Python, FastAPI, TypeScript, React, and PostgreSQL.",
  },
  {
    name: "Elena Rostova",
    skills: ["Python", "PyTorch", "NLP", "Machine Learning", "pgvector", "SentenceTransformers"],
    years_experience: 5.0,
    education_level: 4,
    raw_text: "AI/ML Research Engineer specialized in NLP, PyTorch, and pgvector embeddings.",
  },
  {
    name: "Jordan Smith",
    skills: ["JavaScript", "React", "HTML", "CSS", "Git", "TypeScript"],
    years_experience: 2.0,
    education_level: 3,
    raw_text: "Frontend Developer experienced in React and UI component engineering.",
  },
];

export async function GET(req: NextRequest, { params }: { params: { id: string } }) {
  try {
    const backendUrl = process.env.BACKEND_URL;
    if (backendUrl) {
      try {
        const res = await fetch(`${backendUrl}/api/v1/jobs/${params.id}/matches`, {
          headers: {
            Authorization: req.headers.get("Authorization") || "Bearer demo-token",
          },
        });
        if (res.ok) {
          return NextResponse.json(await res.json());
        }
      } catch (e) {
        console.warn("Backend forward failed, calculating matches locally:", e);
      }
    }

    const job = INITIAL_JOBS.find((j) => j.id === params.id) || INITIAL_JOBS[0];
    const matches = SAMPLE_CANDIDATES.map((cand) =>
      calculateHybridATSScore(cand.raw_text, cand.skills, cand.years_experience, cand.education_level, job)
    );

    matches.sort((a, b) => b.total_score - a.total_score);
    return NextResponse.json(matches);
  } catch (error: any) {
    return NextResponse.json({ detail: error?.message || "Failed to fetch matches" }, { status: 500 });
  }
}
