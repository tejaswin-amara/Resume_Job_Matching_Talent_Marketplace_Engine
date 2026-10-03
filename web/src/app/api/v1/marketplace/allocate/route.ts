import { NextResponse } from "next/server";

export async function POST() {
  return NextResponse.json({
    total_allocated: 3,
    assignments: [
      { candidate_id: "cand_alex_01", job_id: "job_01" },
      { candidate_id: "cand_jordan_02", job_id: "job_02" },
      { candidate_id: "cand_morgan_03", job_id: "job_03" }
    ]
  });
}
