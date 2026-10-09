"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  SpotlightCard,
  AnimatedBadge,
  StarBorder,
  CountUp,
  ShinyText,
  Squares,
} from "@/components/reactbits";
import { ScoreBreakdown } from "@/components/score-breakdown";
import { api, Job, MatchScore } from "@/lib/api";
import { Loader2, Plus, Users, ArrowLeft } from "lucide-react";

export default function RecruiterPortal() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedJob, setSelectedJob] = useState<string | null>(null);
  const [matches, setMatches] = useState<MatchScore[]>([]);
  const [loadingMatches, setLoadingMatches] = useState(false);

  // New Job Form State
  const [showForm, setShowForm] = useState(false);
  const [newJob, setNewJob] = useState({
    title: "",
    department: "",
    description: "",
    requirements: "",
    experienceRange: "",
    skills: "",
  });

  const fetchJobs = async () => {
    try {
      const data = await api.getJobs();
      setJobs(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  const handleSelectJob = async (id: string) => {
    setSelectedJob(id);
    setLoadingMatches(true);
    try {
      const data = await api.getJobMatches(id);
      setMatches(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingMatches(false);
    }
  };

  const handleCreateJob = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createJob({
        title: newJob.title,
        department: newJob.department,
        description: newJob.description,
        requirements: newJob.requirements,
        min_experience: parseInt(newJob.experienceRange) || 0,
        headcount: 1,
        skills: newJob.skills
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean),
      });
      setShowForm(false);
      setNewJob({
        title: "",
        department: "",
        description: "",
        requirements: "",
        experienceRange: "",
        skills: "",
      });
      fetchJobs();
    } catch (e) {
      console.error(e);
      alert("Failed to create job");
    }
  };

  return (
    <div className="relative min-h-screen bg-gray-950 p-8 overflow-hidden">
      <div className="absolute inset-0 z-0 pointer-events-none opacity-30">
        <Squares direction="diagonal" speed={0.3} squareSize={48} borderColor="rgba(255, 255, 255, 0.05)" />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto space-y-8">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-4">
            <Link href="/">
              <StarBorder className="text-xs py-1 px-3">
                <span className="flex items-center gap-1">
                  <ArrowLeft className="w-3.5 h-3.5" /> Home
                </span>
              </StarBorder>
            </Link>
            <h1 className="text-3xl font-bold text-gray-100">
              <ShinyText text="Recruiter Portal" />
            </h1>
          </div>
          <Link href="/recruiter/allocate">
            <StarBorder color="#3b82f6" className="text-xs">
              <span className="flex items-center gap-2">
                <Users className="w-4 h-4 text-blue-400" /> Market Allocation
              </span>
            </StarBorder>
          </Link>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Jobs List */}
          <div className="lg:col-span-1 space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-200">Active Jobs</h2>
              <StarBorder
                onClick={() => setShowForm(!showForm)}
                color="#10b981"
                className="text-xs"
              >
                <span className="flex items-center gap-1">
                  <Plus className="w-4 h-4 text-emerald-400" /> New Job
                </span>
              </StarBorder>
            </div>

            {showForm && (
              <SpotlightCard className="p-6">
                <form onSubmit={handleCreateJob} className="space-y-4">
                  <input
                    className="w-full bg-gray-900 border border-gray-800 rounded p-2 text-sm text-gray-100 focus:outline-none focus:border-blue-500"
                    placeholder="Job Title"
                    value={newJob.title}
                    onChange={(e) => setNewJob({ ...newJob, title: e.target.value })}
                    required
                  />
                  <input
                    className="w-full bg-gray-900 border border-gray-800 rounded p-2 text-sm text-gray-100 focus:outline-none focus:border-blue-500"
                    placeholder="Department"
                    value={newJob.department}
                    onChange={(e) => setNewJob({ ...newJob, department: e.target.value })}
                    required
                  />
                  <textarea
                    className="w-full bg-gray-900 border border-gray-800 rounded p-2 text-sm text-gray-100 h-20 focus:outline-none focus:border-blue-500"
                    placeholder="Description"
                    value={newJob.description}
                    onChange={(e) => setNewJob({ ...newJob, description: e.target.value })}
                    required
                  />
                  <textarea
                    className="w-full bg-gray-900 border border-gray-800 rounded p-2 text-sm text-gray-100 h-20 focus:outline-none focus:border-blue-500"
                    placeholder="Requirements (one per line)"
                    value={newJob.requirements}
                    onChange={(e) => setNewJob({ ...newJob, requirements: e.target.value })}
                  />
                  <input
                    className="w-full bg-gray-900 border border-gray-800 rounded p-2 text-sm text-gray-100 focus:outline-none focus:border-blue-500"
                    placeholder="Experience (e.g. 3-5 years)"
                    value={newJob.experienceRange}
                    onChange={(e) => setNewJob({ ...newJob, experienceRange: e.target.value })}
                  />
                  <input
                    className="w-full bg-gray-900 border border-gray-800 rounded p-2 text-sm text-gray-100 focus:outline-none focus:border-blue-500"
                    placeholder="Skills (comma separated)"
                    value={newJob.skills}
                    onChange={(e) => setNewJob({ ...newJob, skills: e.target.value })}
                    required
                  />
                  <div className="flex justify-end gap-3 pt-2">
                    <button
                      type="button"
                      onClick={() => setShowForm(false)}
                      className="px-3 py-1.5 text-sm text-gray-400 hover:text-gray-200 transition-colors"
                    >
                      Cancel
                    </button>
                    <StarBorder type="submit" color="#10b981" className="text-xs">
                      Create
                    </StarBorder>
                  </div>
                </form>
              </SpotlightCard>
            )}

            {loading ? (
              <div className="flex justify-center p-8">
                <Loader2 className="animate-spin text-blue-500" />
              </div>
            ) : (
              <div className="space-y-3">
                {jobs.map((job) => (
                  <SpotlightCard
                    key={job.id}
                    spotlightColor="rgba(59, 130, 246, 0.2)"
                    className={`p-4 cursor-pointer transition-colors ${
                      selectedJob === job.id
                        ? "border-blue-500 bg-gray-900/90"
                        : "hover:border-gray-700"
                    }`}
                    onClick={() => handleSelectJob(job.id)}
                  >
                    <h3 className="font-semibold text-gray-100">{job.title}</h3>
                    <p className="text-xs text-gray-400">{job.department}</p>
                  </SpotlightCard>
                ))}
              </div>
            )}
          </div>

          {/* Candidate Leaderboard */}
          <div className="lg:col-span-2 space-y-4">
            <h2 className="text-xl font-semibold text-gray-200">Candidate Leaderboard</h2>
            {!selectedJob ? (
              <SpotlightCard className="p-12 text-center text-gray-500">
                Select a job to view ranked candidates.
              </SpotlightCard>
            ) : loadingMatches ? (
              <SpotlightCard className="p-12 flex justify-center">
                <Loader2 className="animate-spin text-blue-500" />
              </SpotlightCard>
            ) : matches.length === 0 ? (
              <SpotlightCard className="p-12 text-center text-gray-500">
                No candidates matched for this job.
              </SpotlightCard>
            ) : (
              <div className="space-y-4">
                {matches.map((match, idx) => (
                  <SpotlightCard key={idx} className="p-6">
                    <div className="flex justify-between items-start mb-6">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-100">
                          {`Candidate ${match.candidate_id.substring(0, 8)}`}
                        </h3>
                        <p className="text-sm text-gray-400">Rank #{idx + 1}</p>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold text-blue-400">
                          <CountUp
                            to={Math.round(match.total_score)}
                            suffix="%"
                          />
                        </div>
                        <div className="text-xs text-gray-500">Overall Match</div>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                      <div>
                        <h4 className="text-sm font-medium text-gray-300 mb-3">
                          Score Breakdown
                        </h4>
                        <ScoreBreakdown score={match} />
                      </div>
                      <div>
                        <h4 className="text-sm font-medium text-gray-300 mb-3">
                          Skills Analysis
                        </h4>
                        <div className="space-y-3">
                          <div>
                            <div className="text-xs text-gray-500 mb-1">Matched Skills</div>
                            <div className="flex flex-wrap gap-1">
                              {match.matched_skills.map((s, i) => (
                                <AnimatedBadge key={i} variant="success">
                                  {s}
                                </AnimatedBadge>
                              ))}
                              {match.matched_skills.length === 0 && (
                                <span className="text-xs text-gray-600">None</span>
                              )}
                            </div>
                          </div>
                          <div>
                            <div className="text-xs text-gray-500 mb-1">Missing Skills</div>
                            <div className="flex flex-wrap gap-1">
                              {match.missing_skills.map((s, i) => (
                                <AnimatedBadge key={i} variant="danger">
                                  {s}
                                </AnimatedBadge>
                              ))}
                              {match.missing_skills.length === 0 && (
                                <span className="text-xs text-gray-600">None</span>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </SpotlightCard>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
