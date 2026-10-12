import { NextRequest, NextResponse } from "next/server";
import { calculateHybridATSScore, extractSkillsFromText, parseFullResume, ServerJob } from "@/lib/server-engine";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { resume_text, job_description } = body;

    const backendUrl = process.env.BACKEND_URL;
    if (backendUrl) {
      try {
        const res = await fetch(`${backendUrl}/api/v1/match/adhoc`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: req.headers.get("Authorization") || "Bearer demo-token",
          },
          body: JSON.stringify(body),
        });
        if (res.ok) {
          const data = await res.json();
          return NextResponse.json(data);
        }
      } catch (e) {
        console.warn("Backend forward failed, computing adhoc match locally:", e);
      }
    }

    const parsedCand = parseFullResume(resume_text || "");
    const candSkills = parsedCand.skills;
    const jobSkills = extractSkillsFromText(job_description || "");

    const virtualJob: ServerJob = {
      id: "adhoc_job",
      title: "Target Role",
      department: "Engineering",
      description: job_description || "",
      requirements: job_description || "",
      min_experience: 3.0,
      headcount: 1,
      skills: jobSkills.length > 0 ? jobSkills : ["Python", "FastAPI", "TypeScript"],
    };

    const matchResult = calculateHybridATSScore(
      resume_text || "",
      candSkills,
      parsedCand.years_experience,
      parsedCand.education_level,
      virtualJob
    );

    return NextResponse.json(matchResult);
  } catch (error: any) {
    return NextResponse.json({ detail: error?.message || "Adhoc match failed" }, { status: 500 });
  }
}
