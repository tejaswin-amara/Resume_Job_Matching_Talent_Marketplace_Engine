import { NextRequest, NextResponse } from "next/server";
import { INITIAL_JOBS, ServerJob } from "@/lib/server-engine";

// In-memory jobs list for serverless state
let customJobs: ServerJob[] = [...INITIAL_JOBS];

export async function GET(req: NextRequest) {
  try {
    const backendUrl = process.env.BACKEND_URL;
    if (backendUrl) {
      try {
        const res = await fetch(`${backendUrl}/api/v1/jobs`, {
          headers: {
            Authorization: req.headers.get("Authorization") || "Bearer demo-token",
          },
        });
        if (res.ok) {
          const data = await res.json();
          const items = Array.isArray(data) ? data : data.items || [];
          return NextResponse.json(items);
        }
      } catch (e) {
        console.warn("Backend forward failed, returning active jobs:", e);
      }
    }

    return NextResponse.json(customJobs);
  } catch (error: any) {
    return NextResponse.json({ detail: error?.message || "Failed to fetch jobs" }, { status: 500 });
  }
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const backendUrl = process.env.BACKEND_URL;
    if (backendUrl) {
      try {
        const res = await fetch(`${backendUrl}/api/v1/jobs`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: req.headers.get("Authorization") || "Bearer demo-token",
          },
          body: JSON.stringify(body),
        });
        if (res.ok) {
          return NextResponse.json(await res.json(), { status: 201 });
        }
      } catch (e) {
        console.warn("Backend forward failed, saving job locally:", e);
      }
    }

    const newJob: ServerJob = {
      id: String(Date.now()),
      title: body.title || "Untitled Role",
      department: body.department || "Engineering",
      description: body.description || "",
      requirements: body.requirements || body.description || "",
      min_experience: Number(body.min_experience || body.min_experience_years || 0),
      max_experience: body.max_experience ? Number(body.max_experience) : undefined,
      location: body.location || "Remote",
      headcount: Number(body.headcount || body.capacity || 1),
      skills: Array.isArray(body.skills) ? body.skills : [],
    };

    customJobs.unshift(newJob);
    return NextResponse.json(newJob, { status: 201 });
  } catch (error: any) {
    return NextResponse.json({ detail: error?.message || "Failed to create job" }, { status: 500 });
  }
}
