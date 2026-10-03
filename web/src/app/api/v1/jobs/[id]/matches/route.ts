import { NextRequest, NextResponse } from "next/server";

export async function GET(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  const jobId = params.id;

  const mockMatches = [
    {
      candidateId: "cand_alex_01",
      candidateName: "Alex Rivera",
      overallScore: 94,
      semanticScore: 96,
      skillScore: 92,
      experienceScore: 90,
      educationScore: 95,
      skillGaps: ["Kubernetes"],
      matchedSkills: ["TypeScript", "React", "Next.js", "PostgreSQL", "Docker"]
    },
    {
      candidateId: "cand_jordan_02",
      candidateName: "Jordan Chen",
      overallScore: 88,
      semanticScore: 85,
      skillScore: 90,
      experienceScore: 86,
      educationScore: 92,
      skillGaps: ["PostgreSQL"],
      matchedSkills: ["TypeScript", "React", "Node.js", "Docker"]
    },
    {
      candidateId: "cand_morgan_03",
      candidateName: "Morgan Taylor",
      overallScore: 78,
      semanticScore: 80,
      skillScore: 75,
      experienceScore: 78,
      educationScore: 85,
      skillGaps: ["Docker", "Next.js"],
      matchedSkills: ["React", "JavaScript", "Git"]
    }
  ];

  return NextResponse.json(mockMatches);
}
