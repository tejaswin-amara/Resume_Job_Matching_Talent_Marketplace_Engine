import { NextRequest, NextResponse } from "next/server";

interface JobItem {
  id: string;
  title: string;
  department: string;
  description: string;
  requirements: string[];
  experienceRange: string;
  skills: string[];
}

const initialJobs: JobItem[] = [
  {
    id: "job_01",
    title: "Senior Full Stack Engineer",
    department: "Engineering",
    description: "Build scalable web applications using Next.js, React, Node.js, and modern cloud databases.",
    requirements: ["3+ years experience with React/Next.js", "Strong TypeScript foundation", "Familiarity with SQL and microservices"],
    experienceRange: "3-6 years",
    skills: ["TypeScript", "React", "Next.js", "Node.js", "PostgreSQL", "Docker"]
  },
  {
    id: "job_02",
    title: "Backend Systems Architect",
    department: "Core Systems",
    description: "Design high-throughput distributed algorithms, graph assignment engines, and data structures.",
    requirements: ["Expert knowledge in Data Structures & Algorithms", "Strong background in Python, Go, or Java", "Experience with scalable REST APIs"],
    experienceRange: "4-7 years",
    skills: ["Python", "FastAPI", "SQL", "Algorithms", "Data Structures", "Docker", "AWS"]
  },
  {
    id: "job_03",
    title: "Machine Learning / NLP Engineer",
    department: "AI & Matching",
    description: "Develop semantic vector embeddings, skill extraction models, and candidate ranking systems.",
    requirements: ["Experience with sentence transformers & vector search", "Strong Python programming", "Knowledge of NLP heuristics and matching algorithms"],
    experienceRange: "2-5 years",
    skills: ["Python", "Machine Learning", "Algorithms", "PostgreSQL", "Linux", "Git"]
  }
];

let globalJobs = [...initialJobs];

export async function GET() {
  return NextResponse.json({
    items: globalJobs,
    total: globalJobs.length
  });
}

export async function POST(req: NextRequest) {
  try {
    const data = await req.json();
    const newJob: JobItem = {
      id: "job_" + Math.random().toString(36).substring(2, 9),
      title: data.title || "Untitled Role",
      department: data.department || "General",
      description: data.description || "",
      requirements: Array.isArray(data.requirements) ? data.requirements : [data.requirements],
      experienceRange: data.experienceRange || "2-5 years",
      skills: Array.isArray(data.skills) ? data.skills : (data.skills || "").split(",").map((s: string) => s.trim()).filter(Boolean)
    };
    globalJobs = [newJob, ...globalJobs];
    return NextResponse.json(newJob);
  } catch (error: any) {
    return NextResponse.json({ error: error.message || "Failed to create job" }, { status: 500 });
  }
}
