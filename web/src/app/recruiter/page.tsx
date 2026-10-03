"use client";
import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScoreBreakdown } from "@/components/score-breakdown";
import { api, Job, MatchScore } from "@/lib/api";
import { Loader2, Plus, Users } from "lucide-react";

export default function RecruiterPortal() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedJob, setSelectedJob] = useState<string | null>(null);
  const [matches, setMatches] = useState<MatchScore[]>([]);
  const [loadingMatches, setLoadingMatches] = useState(false);

  // New Job Form State
  const [showForm, setShowForm] = useState(false);
  const [newJob, setNewJob] = useState({
    title: "", department: "", description: "", requirements: "", experienceRange: "", skills: ""
  });

  const fetchJobs = async () => {
    try {
      const data = await api.getJobs();
      setJobs(data.items);
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
        requirements: newJob.requirements.split("\n").filter(Boolean),
        experienceRange: newJob.experienceRange,
        skills: newJob.skills.split(",").map(s => s.trim()).filter(Boolean)
      });
      setShowForm(false);
      fetchJobs();
    } catch (e) {
      console.error(e);
      alert("Failed to create job");
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-100">Recruiter Portal</h1>
          <Link href="/recruiter/allocate">
            <Button variant="outline" className="flex items-center gap-2">
              <Users className="w-4 h-4" /> Market Allocation
            </Button>
          </Link>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Jobs List */}
          <div className="lg:col-span-1 space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-200">Active Jobs</h2>
              <Button size="sm" onClick={() => setShowForm(!showForm)}>
                <Plus className="w-4 h-4 mr-1" /> New Job
              </Button>
            </div>

            {showForm && (
              <Card>
                <CardContent className="pt-6">
                  <form onSubmit={handleCreateJob} className="space-y-4">
                    <input className="w-full bg-gray-900 border border-gray-800 rounded p-2 text-sm text-gray-100" placeholder="Job Title" value={newJob.title} onChange={e => setNewJob({...newJob, title: e.target.value})} required />
                    <input className="w-full bg-gray-900 border border-gray-800 rounded p-2 text-sm text-gray-100" placeholder="Department" value={newJob.department} onChange={e => setNewJob({...newJob, department: e.target.value})} required />
                    <textarea className="w-full bg-gray-900 border border-gray-800 rounded p-2 text-sm text-gray-100 h-20" placeholder="Description" value={newJob.description} onChange={e => setNewJob({...newJob, description: e.target.value})} required />
                    <textarea className="w-full bg-gray-900 border border-gray-800 rounded p-2 text-sm text-gray-100 h-20" placeholder="Requirements (one per line)" value={newJob.requirements} onChange={e => setNewJob({...newJob, requirements: e.target.value})} />
                    <input className="w-full bg-gray-900 border border-gray-800 rounded p-2 text-sm text-gray-100" placeholder="Experience (e.g. 3-5 years)" value={newJob.experienceRange} onChange={e => setNewJob({...newJob, experienceRange: e.target.value})} />
                    <input className="w-full bg-gray-900 border border-gray-800 rounded p-2 text-sm text-gray-100" placeholder="Skills (comma separated)" value={newJob.skills} onChange={e => setNewJob({...newJob, skills: e.target.value})} required />
                    <div className="flex justify-end gap-2">
                      <Button type="button" variant="ghost" onClick={() => setShowForm(false)}>Cancel</Button>
                      <Button type="submit">Create</Button>
                    </div>
                  </form>
                </CardContent>
              </Card>
            )}

            {loading ? (
              <div className="flex justify-center p-8"><Loader2 className="animate-spin text-blue-500" /></div>
            ) : (
              <div className="space-y-3">
                {jobs.map(job => (
                  <Card 
                    key={job.id} 
                    className={`cursor-pointer transition-colors hover:border-blue-500 ${selectedJob === job.id ? 'border-blue-500 bg-gray-900/80' : ''}`}
                    onClick={() => handleSelectJob(job.id)}
                  >
                    <CardContent className="p-4">
                      <h3 className="font-semibold text-gray-100">{job.title}</h3>
                      <p className="text-xs text-gray-400">{job.department}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>

          {/* Candidate Leaderboard */}
          <div className="lg:col-span-2 space-y-4">
            <h2 className="text-xl font-semibold text-gray-200">Candidate Leaderboard</h2>
            {!selectedJob ? (
              <Card><CardContent className="p-12 text-center text-gray-500">Select a job to view ranked candidates.</CardContent></Card>
            ) : loadingMatches ? (
              <Card><CardContent className="p-12 flex justify-center"><Loader2 className="animate-spin text-blue-500" /></CardContent></Card>
            ) : matches.length === 0 ? (
              <Card><CardContent className="p-12 text-center text-gray-500">No candidates matched for this job.</CardContent></Card>
            ) : (
              <div className="space-y-4">
                {matches.map((match, idx) => (
                  <Card key={idx}>
                    <CardContent className="p-6">
                      <div className="flex justify-between items-start mb-6">
                        <div>
                          <h3 className="text-lg font-semibold text-gray-100">{match.candidateName || `Candidate ${match.candidateId.substring(0,8)}`}</h3>
                          <p className="text-sm text-gray-400">Rank #{idx + 1}</p>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-bold text-blue-400">{(match.overallScore * 100).toFixed(0)}%</div>
                          <div className="text-xs text-gray-500">Overall Match</div>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        <div>
                          <h4 className="text-sm font-medium text-gray-300 mb-3">Score Breakdown</h4>
                          <ScoreBreakdown score={match} />
                        </div>
                        <div>
                          <h4 className="text-sm font-medium text-gray-300 mb-3">Skills Analysis</h4>
                          <div className="space-y-3">
                            <div>
                              <div className="text-xs text-gray-500 mb-1">Matched Skills</div>
                              <div className="flex flex-wrap gap-1">
                                {match.matchedSkills.map((s, i) => <Badge key={i} variant="success">{s}</Badge>)}
                                {match.matchedSkills.length === 0 && <span className="text-xs text-gray-600">None</span>}
                              </div>
                            </div>
                            <div>
                              <div className="text-xs text-gray-500 mb-1">Missing Skills</div>
                              <div className="flex flex-wrap gap-1">
                                {match.skillGaps.map((s, i) => <Badge key={i} variant="danger">{s}</Badge>)}
                                {match.skillGaps.length === 0 && <span className="text-xs text-gray-600">None</span>}
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
