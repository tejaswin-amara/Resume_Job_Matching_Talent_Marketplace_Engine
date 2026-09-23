'use client';

import { RadialScoreMeter } from '@/components/feedback/radial-score-meter';
import { ResumeDropzone } from '@/components/feedback/resume-dropzone';
import { SkillGapVisualizer } from '@/components/feedback/skill-gap-visualizer';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import type { CandidateEvaluation, JobProfile } from '@/contracts/match-engine.schema';
import { apiClient } from '@/lib/api-client';
import { useMutation, useQuery } from '@tanstack/react-query';
import {
  Brain,
  CheckCircle,
  Clock,
  HelpCircle,
  Mail,
  Sparkles,
  Target,
  User,
  Zap,
} from 'lucide-react';
import { useSearchParams } from 'next/navigation';
import * as React from 'react';

function MatchStudioContent() {
  const searchParams = useSearchParams();
  const initialJobId = searchParams.get('jobId') || undefined;

  const [selectedJobId, setSelectedJobId] = React.useState<string | undefined>(initialJobId);
  const [currentEvaluation, setCurrentEvaluation] = React.useState<CandidateEvaluation | null>(
    null,
  );
  const [analysisStep, setAnalysisStep] = React.useState<1 | 2 | 3>(1);

  // Fetch available jobs
  const { data: jobs = [] } = useQuery<JobProfile[]>({
    queryKey: ['jobs'],
    queryFn: () => apiClient.getJobs(),
  });

  React.useEffect(() => {
    if (!selectedJobId && jobs.length > 0) {
      setSelectedJobId(jobs[0].id);
    }
  }, [jobs, selectedJobId]);

  // Pre-seed default evaluation if none is present
  React.useEffect(() => {
    if (!currentEvaluation) {
      apiClient.getEvaluation('e0000000-0000-4000-8000-000000000001').then((res) => {
        setCurrentEvaluation(res);
      });
    }
  }, [currentEvaluation]);

  const activeJob = jobs.find((j) => j.id === selectedJobId) || jobs[0];

  // Resume evaluation mutation
  const evaluationMutation = useMutation({
    mutationFn: async (file: File) => {
      setAnalysisStep(1);
      const step1Timer = setTimeout(() => setAnalysisStep(2), 250);
      const step2Timer = setTimeout(() => setAnalysisStep(3), 500);

      try {
        const result = await apiClient.evaluateResume(file, selectedJobId);
        return result;
      } finally {
        clearTimeout(step1Timer);
        clearTimeout(step2Timer);
      }
    },
    onSuccess: (data) => {
      setCurrentEvaluation(data);
    },
  });

  const handleFileDrop = (file: File) => {
    evaluationMutation.mutate(file);
  };

  const metrics = currentEvaluation?.matchMetrics;

  return (
    <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-semibold uppercase tracking-wider text-blue-400">
              Match Intelligence Studio
            </span>
            <Badge variant="outline" className="text-[10px] border-blue-500/30 text-blue-300">
              SBERT &bull; v2.4
            </Badge>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
            Autonomous Candidate Calibration
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Ingest candidate documents, align semantic skill vectors, and review diagnostic LLM
            feedback.
          </p>
        </div>

        {/* Job Requisition Selector */}
        <div className="flex items-center gap-3">
          <label
            htmlFor="job-selector"
            className="text-xs text-slate-400 font-medium whitespace-nowrap"
          >
            Target Requisition:
          </label>
          <select
            id="job-selector"
            aria-label="Target Requisition"
            value={selectedJobId || ''}
            onChange={(e) => setSelectedJobId(e.target.value)}
            className="h-10 rounded-lg border border-slate-700 bg-slate-900 px-3 text-xs text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 max-w-[280px]"
          >
            {jobs.map((job) => (
              <option key={job.id} value={job.id}>
                {job.title} ({job.department})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Split-View Dashboard Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Pane: Document Ingestion & Target Role Specs (lg:col-span-5) */}
        <div className="lg:col-span-5 space-y-6">
          {/* Dropzone Card */}
          <Card className="border-slate-800 bg-slate-900/60">
            <CardHeader className="pb-3">
              <CardTitle className="text-base font-semibold text-white flex items-center gap-2">
                <Zap className="h-4 w-4 text-blue-400" />
                Document Ingestion Pane
              </CardTitle>
              <CardDescription className="text-xs">
                Upload resume files to trigger multi-stage NLP vector pipeline
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResumeDropzone
                onFileAccepted={handleFileDrop}
                isLoading={evaluationMutation.isPending}
                currentStep={analysisStep}
              />
            </CardContent>
          </Card>

          {/* Active Target Requisition Summary */}
          {activeJob && (
            <Card className="border-slate-800 bg-slate-900/40">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <Badge variant="secondary" className="text-[10px] font-mono">
                    {activeJob.department}
                  </Badge>
                  <Badge variant="outline" className="text-[10px]">
                    {activeJob.experienceLevel} Level
                  </Badge>
                </div>
                <CardTitle className="text-base text-white mt-1">{activeJob.title}</CardTitle>
                <CardDescription className="text-xs line-clamp-3">
                  {activeJob.rawDescription}
                </CardDescription>
              </CardHeader>

              <CardContent className="pt-0">
                <div className="text-xs font-medium text-slate-400 mb-2">
                  Mandatory Competencies:
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {activeJob.requiredSkills.map((skill) => (
                    <span
                      key={skill}
                      className="rounded-md border border-slate-700/60 bg-slate-800/80 px-2.5 py-0.5 text-xs text-slate-300"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Candidate Profile Quick Info */}
          {currentEvaluation && (
            <Card className="border-slate-800 bg-slate-900/40">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-semibold text-slate-300 flex items-center gap-2">
                  <User className="h-4 w-4 text-slate-400" />
                  Candidate Metadata
                </CardTitle>
              </CardHeader>
              <CardContent className="text-xs space-y-2 text-slate-400">
                <div className="flex items-center justify-between">
                  <span className="text-slate-500">Name:</span>
                  <span className="font-semibold text-slate-200">{currentEvaluation.name}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-500 flex items-center gap-1">
                    <Mail className="h-3 w-3" /> Email:
                  </span>
                  <span className="font-mono text-slate-300">{currentEvaluation.email}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-500 flex items-center gap-1">
                    <Clock className="h-3 w-3" /> Parsed:
                  </span>
                  <span className="font-mono text-slate-300">
                    {new Date(currentEvaluation.parsedAt).toLocaleTimeString()}
                  </span>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Right Pane: Deep Semantic Evaluation Report (lg:col-span-7) */}
        <div className="lg:col-span-7 space-y-6">
          {metrics ? (
            <>
              {/* Top Row: Radial Gauge + 3 Metric Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-12 gap-4 items-stretch">
                {/* Gauge Card */}
                <Card className="sm:col-span-5 border-slate-800 bg-slate-900/60 flex flex-col items-center justify-center p-6 text-center">
                  <RadialScoreMeter score={metrics.overallScore} size={150} />
                </Card>

                {/* 3 Metric Cards (sm:col-span-7) */}
                <div className="sm:col-span-7 flex flex-col justify-between gap-3">
                  <Card className="border-slate-800 bg-slate-900/50 p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className="h-8 w-8 rounded-lg bg-blue-500/10 flex items-center justify-center text-blue-400 border border-blue-500/20">
                          <Brain className="h-4 w-4" />
                        </div>
                        <div>
                          <div className="text-xs font-medium text-slate-400">
                            Semantic Similarity
                          </div>
                          <div className="text-lg font-bold text-white">
                            {metrics.semanticSimilarity}%
                          </div>
                        </div>
                      </div>
                      <Badge
                        variant="outline"
                        className="text-[10px] text-blue-400 border-blue-500/30"
                      >
                        Sentence-BERT
                      </Badge>
                    </div>
                  </Card>

                  <Card className="border-slate-800 bg-slate-900/50 p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className="h-8 w-8 rounded-lg bg-indigo-500/10 flex items-center justify-center text-indigo-400 border border-indigo-500/20">
                          <Target className="h-4 w-4" />
                        </div>
                        <div>
                          <div className="text-xs font-medium text-slate-400">Keyword Density</div>
                          <div className="text-lg font-bold text-white">
                            {metrics.keywordDensityScore}%
                          </div>
                        </div>
                      </div>
                      <Badge
                        variant="outline"
                        className="text-[10px] text-indigo-400 border-indigo-500/30"
                      >
                        TF-IDF Rank
                      </Badge>
                    </div>
                  </Card>

                  <Card className="border-slate-800 bg-slate-900/50 p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className="h-8 w-8 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-400 border border-emerald-500/20">
                          <CheckCircle className="h-4 w-4" />
                        </div>
                        <div>
                          <div className="text-xs font-medium text-slate-400">
                            Experience Calibration
                          </div>
                          <div className="text-lg font-bold text-white">
                            {metrics.experienceMatchScore}%
                          </div>
                        </div>
                      </div>
                      <Badge
                        variant="outline"
                        className="text-[10px] text-emerald-400 border-emerald-500/30"
                      >
                        Seniority Fit
                      </Badge>
                    </div>
                  </Card>
                </div>
              </div>

              {/* Skill Gap Visualizer Component */}
              <SkillGapVisualizer
                skillAssessments={metrics.skillAssessments}
                sharedSkills={metrics.sharedSkills}
                missingCoreSkills={metrics.missingCoreSkills}
              />

              {/* LLM Synthesis Callout Card */}
              <Card className="border-slate-800 bg-gradient-to-br from-slate-900/90 to-blue-950/20 border-l-4 border-l-blue-500">
                <CardHeader className="pb-3">
                  <div className="flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-blue-400" />
                    <CardTitle className="text-base text-white">
                      Automated LLM Synthesis &amp; Interview Calibration
                    </CardTitle>
                  </div>
                  <CardDescription className="text-xs text-slate-300 leading-relaxed pt-1">
                    {metrics.llmFeedback.summary}
                  </CardDescription>
                </CardHeader>

                <CardContent className="space-y-4 pt-0">
                  {/* Extracted Strengths */}
                  <div>
                    <h4 className="text-xs font-semibold uppercase tracking-wider text-emerald-400 mb-2">
                      Validated Strengths &amp; Engineering Signals
                    </h4>
                    <ul className="space-y-1.5 text-xs text-slate-300">
                      {metrics.llmFeedback.strengths.map((str) => (
                        <li key={str} className="flex items-start gap-2">
                          <span className="text-emerald-400 font-bold">&bull;</span>
                          <span>{str}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Actionable Interview Questions */}
                  <div>
                    <h4 className="text-xs font-semibold uppercase tracking-wider text-blue-400 mb-2 flex items-center gap-1.5">
                      <HelpCircle className="h-3.5 w-3.5" />
                      Recommended Technical Interview Inquiries
                    </h4>
                    <ul className="space-y-2 text-xs">
                      {metrics.llmFeedback.interviewQuestions.map((q) => (
                        <li
                          key={q}
                          className="rounded-lg border border-slate-800 bg-slate-900/80 p-2.5 text-slate-200"
                        >
                          <span className="font-semibold text-blue-400 mr-1.5">Prompt:</span>
                          {q}
                        </li>
                      ))}
                    </ul>
                  </div>
                </CardContent>
              </Card>
            </>
          ) : (
            <Card className="border-slate-800 bg-slate-900/40 p-12 text-center">
              <p className="text-sm text-slate-400">
                Upload a candidate resume on the left to compute and view semantic match
                intelligence.
              </p>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

export default function CandidatesPage() {
  return (
    <React.Suspense
      fallback={
        <div className="container mx-auto px-4 py-16 text-center text-slate-400 text-sm">
          Loading Match Intelligence Studio...
        </div>
      }
    >
      <MatchStudioContent />
    </React.Suspense>
  );
}
