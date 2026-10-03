import { NextResponse } from "next/server";

export async function POST() {
  return NextResponse.json({
    unfilled_demand: ["job_02_backend_lead", "job_03_ai_specialist"],
    unutilized_supply: ["cand_taylor_04", "cand_sam_05"]
  });
}
