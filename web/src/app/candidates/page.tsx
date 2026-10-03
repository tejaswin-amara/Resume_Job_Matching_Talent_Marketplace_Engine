"use client";
import React, { useState, useEffect } from "react";
import { UploadDropzone } from "@/components/upload-dropzone";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScoreBreakdown } from "@/components/score-breakdown";
import { api, ParsedResume, Job, MatchScore } from "@/lib/api";
import { Loader2 } from "lucide-react";

export default function CandidatePortal() {
  const [uploading, setUploading] = useState(false);
  const [resumeData, setResumeData] = useState<ParsedResume | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [matches, setMatches] = useState<Record<string, MatchScore>>({});
  const [loadingJobs, setLoadingJobs] = useState(false);

  useEffect(() => {
    if (resumeData) {
      fetchJobs();
    }
  }, [resumeData]);

  const fetchJobs = async () => {
    setLoadingJobs(true);
    try {
      const data = await api.getJobs();
      setJobs(data.items);
      // For each job, calculate adhoc match
      const newMatches: Record<string, MatchScore> = {};
      for (const job of data.items) {
        try {
          const match = await api.adhocMatch(resumeData!.rawText, `${job.title}\n${job.description}\n${job.requirements.join(', ')}`);
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
      // In a real app we'd upload the file to get parsed text. Here we assume API extracts it.
      const res = await api.uploadResume(file);
      // fallback to parse-text if upload doesn't return full parsed
      if (res.text) {
        const parsed = await api.parseText(res.text);
        setResumeData(parsed);
      } else {
        setResumeData(res);
      }
    } catch (error) {
      console.error("Upload failed", error);
      alert("Upload failed. Check console.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        <h1 className="text-3xl font-bold text-gray-100">Candidate Portal</h1>
        
        {!resumeData && (
          <Card>
            <CardHeader>
              <CardTitle>Upload Resume</CardTitle>
            </CardHeader>
            <CardContent>
              {uploading ? (
                <div className="flex flex-col items-center justify-center p-12">
                  <Loader2 className="h-8 w-8 animate-spin text-blue-500 mb-4" />
                  <p className="text-gray-400">Processing resume...</p>
                </div>
              ) : (
                <UploadDropzone onUpload={handleUpload} />
              )}
            </CardContent>
          </Card>
        )}

        {resumeData && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="md:col-span-1 space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Your Profile</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="mb-4">
                    <h4 className="text-sm font-semibold text-gray-400 mb-2">Skills Extracted</h4>
                    <div className="flex flex-wrap gap-2">
                      {resumeData.skills.map((s, i) => (
                        <Badge key={i} variant="outline">{s}</Badge>
                      ))}
                    </div>
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-gray-400 mb-2">Experience</h4>
                    <p className="text-sm text-gray-300">{resumeData.experience.length} roles found</p>
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="md:col-span-2 space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Matching Jobs</CardTitle>
                </CardHeader>
                <CardContent>
                  {loadingJobs ? (
                    <div className="flex justify-center p-8">
                      <Loader2 className="h-6 w-6 animate-spin text-blue-500" />
                    </div>
                  ) : jobs.length === 0 ? (
                    <p className="text-gray-400 text-center p-8">No jobs available.</p>
                  ) : (
                    <div className="space-y-6">
                      {jobs.map(job => {
                        const match = matches[job.id];
                        return (
                          <div key={job.id} className="p-4 border border-gray-800 rounded-lg bg-gray-900/50">
                            <h3 className="text-xl font-semibold text-blue-400 mb-1">{job.title}</h3>
                            <p className="text-sm text-gray-400 mb-4">{job.department}</p>
                            
                            {match ? (
                              <div className="space-y-4">
                                <ScoreBreakdown score={match} />
                                
                                <div>
                                  <h4 className="text-xs font-semibold text-gray-500 mb-2 uppercase">Skill Match</h4>
                                  <div className="flex flex-wrap gap-2">
                                    {match.matchedSkills.map((s, i) => (
                                      <Badge key={`m-${i}`} variant="success">{s}</Badge>
                                    ))}
                                    {match.skillGaps.map((s, i) => (
                                      <Badge key={`g-${i}`} variant="danger">{s}</Badge>
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
                          </div>
                        );
                      })}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
