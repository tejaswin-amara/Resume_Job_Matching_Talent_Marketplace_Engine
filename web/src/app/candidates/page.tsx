"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { UploadDropzone } from "@/components/upload-dropzone";
import {
  SpotlightCard,
  AnimatedBadge,
  StarBorder,
  ShinyText,
  Squares,
} from "@/components/reactbits";
import { ScoreBreakdown } from "@/components/score-breakdown";
import { api, ParsedResume, Job, MatchScore } from "@/lib/api";
import { Loader2, ArrowLeft } from "lucide-react";

export default function CandidatePortal() {
  const [uploading, setUploading] = useState(false);
  const [resumeData, setResumeData] = useState<(ParsedResume & { id: string }) | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [matches, setMatches] = useState<Record<string, MatchScore>>({});
  const [loadingJobs, setLoadingJobs] = useState(false);

  useEffect(() => {
    if (resumeData) {
      fetchJobs();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [resumeData]);

  const fetchJobs = async () => {
    if (!resumeData) return;
    setLoadingJobs(true);
    try {
      const data = await api.getJobs();
      setJobs(data);
      // For each job, calculate adhoc match
      const newMatches: Record<string, MatchScore> = {};
      for (const job of data) {
        try {
          const match = await api.adhocMatch(
            resumeData.id,
            job.id
          );
          newMatches[job.id] = match;
        } catch (e) {
          console.error("Match error for job", job.id, e);
        }
      }
      setMatches(newMatches);
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingJobs(false);
    }
  };

  const handleUpload = async (file: File) => {
    setUploading(true);
    try {
      const res = await api.uploadResume(file);
      setResumeData({ id: res.id, skills: res.skills_extracted });
    } catch (error) {
      console.error("Upload failed", error);
      alert("Upload failed. Check console.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="relative min-h-screen bg-gray-950 p-8 overflow-hidden">
      <div className="absolute inset-0 z-0 pointer-events-none opacity-30">
        <Squares direction="diagonal" speed={0.3} squareSize={48} borderColor="rgba(255, 255, 255, 0.05)" />
      </div>

      <div className="relative z-10 max-w-6xl mx-auto space-y-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/">
              <StarBorder className="text-xs py-1 px-3">
                <span className="flex items-center gap-1">
                  <ArrowLeft className="w-3.5 h-3.5" /> Back
                </span>
              </StarBorder>
            </Link>
            <h1 className="text-3xl font-bold text-gray-100">
              <ShinyText text="Candidate Portal" />
            </h1>
          </div>
        </div>

        {!resumeData && (
          <SpotlightCard className="p-6">
            <h2 className="text-xl font-semibold text-gray-100 mb-4">Upload Resume</h2>
            {uploading ? (
              <div className="flex flex-col items-center justify-center p-12">
                <Loader2 className="h-8 w-8 animate-spin text-blue-500 mb-4" />
                <p className="text-gray-400">Processing resume...</p>
              </div>
            ) : (
              <UploadDropzone onUpload={handleUpload} />
            )}
          </SpotlightCard>
        )}

        {resumeData && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="md:col-span-1 space-y-6">
              <SpotlightCard className="p-6">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-xl font-semibold text-gray-100">Your Profile</h2>
                  <StarBorder onClick={() => setResumeData(null)} className="text-xs">
                    Re-upload
                  </StarBorder>
                </div>
                <div className="mb-4">
                  <h4 className="text-sm font-semibold text-gray-400 mb-2">Skills Extracted</h4>
                  <div className="flex flex-wrap gap-2">
                    {resumeData.skills.map((s, i) => (
                      <AnimatedBadge key={i} variant="outline">
                        {s}
                      </AnimatedBadge>
                    ))}
                  </div>
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-gray-400 mb-2">Experience</h4>
                  <p className="text-sm text-gray-300">Experience data is unavailable</p>
                </div>
              </SpotlightCard>
            </div>

            <div className="md:col-span-2 space-y-6">
              <SpotlightCard className="p-6">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-semibold text-gray-100">Matching Jobs</h2>
                  <StarBorder onClick={fetchJobs} disabled={loadingJobs} className="text-xs">
                    Refresh Matches
                  </StarBorder>
                </div>
                {loadingJobs ? (
                  <div className="flex justify-center p-8">
                    <Loader2 className="h-6 w-6 animate-spin text-blue-500" />
                  </div>
                ) : jobs.length === 0 ? (
                  <p className="text-gray-400 text-center p-8">No jobs available.</p>
                ) : (
                  <div className="space-y-6">
                    {jobs.map((job) => {
                      const match = matches[job.id];
                      return (
                        <SpotlightCard
                          key={job.id}
                          spotlightColor="rgba(59, 130, 246, 0.15)"
                          className="p-5 border border-gray-800 bg-gray-900/50"
                        >
                          <h3 className="text-xl font-semibold text-blue-400 mb-1">{job.title}</h3>
                          <p className="text-sm text-gray-400 mb-4">{job.department}</p>

                          {match ? (
                            <div className="space-y-4">
                              <ScoreBreakdown score={match} />

                              <div>
                                <h4 className="text-xs font-semibold text-gray-500 mb-2 uppercase">
                                  Skill Match
                                </h4>
                                <div className="flex flex-wrap gap-2">
                                  {match.matched_skills.map((s, i) => (
                                    <AnimatedBadge key={`m-${i}`} variant="success">
                                      {s}
                                    </AnimatedBadge>
                                  ))}
                                  {match.missing_skills.map((s, i) => (
                                    <AnimatedBadge key={`g-${i}`} variant="danger">
                                      {s}
                                    </AnimatedBadge>
                                  ))}
                                </div>
                              </div>
                            </div>
                          ) : (
                            <div className="flex items-center space-x-2 text-gray-500 text-sm">
                              <Loader2 className="h-4 w-4 animate-spin" />
                              <span>Calculating match...</span>
                            </div>
                          )}
                        </SpotlightCard>
                      );
                    })}
                  </div>
                )}
              </SpotlightCard>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
