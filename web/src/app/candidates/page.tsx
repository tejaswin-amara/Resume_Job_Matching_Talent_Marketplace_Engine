"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { UploadDropzone } from "@/components/reactbits/UploadDropzone";
import {
  SpotlightCard,
  AnimatedBadge,
  StarBorder,
  ShinyText,
  Squares,
} from "@/components/reactbits";
import { ScoreBreakdown } from "@/components/score-breakdown";
import { api, ParsedResume, Job, MatchScore } from "@/lib/api";
import { Loader2, ArrowLeft, Mail, Phone, MapPin, Briefcase, GraduationCap, User } from "lucide-react";

export default function CandidatePortal() {
  const [uploading, setUploading] = useState(false);
  const [resumeData, setResumeData] = useState<ParsedResume | null>(null);
  const [rawResumeText, setRawResumeText] = useState("");
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
    setLoadingJobs(true);
    try {
      const data = await api.getJobs();
      setJobs(data);
      // For each job, calculate adhoc match
      const newMatches: Record<string, MatchScore> = {};
      for (const job of data) {
        try {
          const match = await api.adhocMatch(
            rawResumeText,
            `${job.title}\n${job.description}\n${job.requirements}`
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
      setResumeData(res);
      setRawResumeText(res.raw_text || "");
    } catch (error: any) {
      console.error("Upload failed", error);
      alert(error?.message || "Upload failed. Please check the file format.");
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
              <SpotlightCard className="p-6 space-y-5">
                <div className="flex justify-between items-start">
                  <div>
                    <h2 className="text-xl font-bold text-gray-100 flex items-center gap-2">
                      <User className="w-5 h-5 text-blue-400" />
                      {resumeData.name || "Candidate Profile"}
                    </h2>
                    <span className="inline-block mt-1 text-xs px-2.5 py-0.5 rounded-full bg-blue-500/15 text-blue-300 font-medium border border-blue-500/20">
                      {resumeData.years_experience ?? 0} yrs experience
                    </span>
                  </div>
                  <StarBorder onClick={() => setResumeData(null)} className="text-xs">
                    Re-upload
                  </StarBorder>
                </div>

                {/* Contact Information */}
                {(resumeData.email || resumeData.phone || resumeData.location) && (
                  <div className="space-y-1.5 pt-1 border-t border-gray-800/80 text-xs text-gray-300">
                    {resumeData.email && (
                      <div className="flex items-center gap-2 text-gray-300">
                        <Mail className="w-3.5 h-3.5 text-blue-400 shrink-0" />
                        <span className="truncate">{resumeData.email}</span>
                      </div>
                    )}
                    {resumeData.phone && (
                      <div className="flex items-center gap-2 text-gray-300">
                        <Phone className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                        <span>{resumeData.phone}</span>
                      </div>
                    )}
                    {resumeData.location && (
                      <div className="flex items-center gap-2 text-gray-300">
                        <MapPin className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                        <span>{resumeData.location}</span>
                      </div>
                    )}
                  </div>
                )}

                {/* Skills Extracted */}
                <div className="pt-2 border-t border-gray-800/80">
                  <div className="flex items-center justify-between mb-2.5">
                    <h4 className="text-sm font-semibold text-gray-300">Skills Extracted</h4>
                    <span className="text-xs text-gray-500 font-mono">({resumeData.skills.length})</span>
                  </div>
                  <div className="flex flex-wrap gap-1.5 max-h-48 overflow-y-auto pr-1">
                    {resumeData.skills.map((s, i) => (
                      <AnimatedBadge key={i} variant="outline" className="text-xs">
                        {s}
                      </AnimatedBadge>
                    ))}
                  </div>
                </div>

                {/* Experience / Roles */}
                <div className="pt-2 border-t border-gray-800/80">
                  <div className="flex items-center justify-between mb-2.5">
                    <h4 className="text-sm font-semibold text-gray-300 flex items-center gap-1.5">
                      <Briefcase className="w-4 h-4 text-blue-400" />
                      Work Experience
                    </h4>
                    <span className="text-xs text-gray-400">
                      {resumeData.roles?.length || 0} {resumeData.roles?.length === 1 ? "role" : "roles"}
                    </span>
                  </div>
                  {resumeData.roles && resumeData.roles.length > 0 ? (
                    <div className="space-y-2.5">
                      {resumeData.roles.map((role, idx) => (
                        <div key={idx} className="p-3 rounded-lg bg-gray-900/60 border border-gray-800/80 text-xs space-y-1">
                          <div className="font-semibold text-gray-200 flex items-start justify-between gap-2">
                            <span>{role.title}</span>
                            <span className="text-gray-400 text-[11px] font-normal whitespace-nowrap">{role.duration}</span>
                          </div>
                          {role.company && <div className="text-gray-400 text-[11px]">{role.company}</div>}
                          {role.description && <div className="text-gray-400 text-[11px] leading-relaxed">{role.description}</div>}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-xs text-gray-400">General software engineering background.</p>
                  )}
                </div>

                {/* Education */}
                {resumeData.education && resumeData.education.length > 0 && (
                  <div className="pt-2 border-t border-gray-800/80">
                    <h4 className="text-sm font-semibold text-gray-300 mb-2.5 flex items-center gap-1.5">
                      <GraduationCap className="w-4 h-4 text-purple-400" />
                      Education
                    </h4>
                    <div className="space-y-2">
                      {resumeData.education.map((edu, idx) => (
                        <div key={idx} className="p-2.5 rounded-lg bg-gray-900/60 border border-gray-800/80 text-xs">
                          <div className="font-medium text-gray-200">
                            {edu.degree}{edu.field ? ` in ${edu.field}` : ''}
                          </div>
                          <div className="text-gray-400 text-[11px] flex justify-between mt-0.5">
                            <span>{edu.institution || 'University'}</span>
                            {edu.year && <span>{edu.year}</span>}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
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
