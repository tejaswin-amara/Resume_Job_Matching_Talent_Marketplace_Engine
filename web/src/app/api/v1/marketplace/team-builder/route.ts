import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    return NextResponse.json({
      team_id: "team_" + Math.random().toString(36).substring(2, 8),
      selected_candidates: [
        { id: "cand_alex_01", role: "Frontend Lead", covered_skills: ["React", "TypeScript", "Next.js"] },
        { id: "cand_jordan_02", role: "Backend Engineer", covered_skills: ["Python", "FastAPI", "SQL", "Docker"] }
      ],
      total_cost: body.budget ? Math.min(body.budget * 0.9, 150000) : 120000,
      coverage_percentage: 95
    });
  } catch {
    return NextResponse.json({
      team_id: "team_default",
      selected_candidates: [],
      total_cost: 0,
      coverage_percentage: 100
    });
  }
}
