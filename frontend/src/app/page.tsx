import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { apiClient } from '@/lib/api-client';
import {
  ArrowRight,
  Binary,
  Bot,
  BrainCircuit,
  Briefcase,
  CheckCircle2,
  FileCheck2,
  Layers,
  Sparkles,
  Zap,
} from 'lucide-react';
import Link from 'next/link';

export default async function HomePage() {
  const jobs = await apiClient.getJobs().catch(() => []);

  return (
    <div className="flex flex-col min-h-full">
      {/* Hero Section */}
      <section className="relative overflow-hidden py-16 sm:py-24 border-b border-slate-900 bg-gradient-to-b from-slate-950 via-slate-900/50 to-slate-950">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(59,130,246,0.15),rgba(255,255,255,0))]" />

        <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center max-w-4xl">
          <Badge
            variant="outline"
            className="mb-4 py-1.5 px-3.5 text-xs font-semibold tracking-wide border-blue-500/30 bg-blue-950/40 text-blue-300 backdrop-blur-sm"
          >
            <Sparkles className="h-3.5 w-3.5 mr-1.5 text-blue-400" />
            Next-Gen Talent Engine &bull; Sentence-BERT &amp; Min-Cost Flow
          </Badge>

          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white leading-tight">
            Autonomous AI Resume &amp;{' '}
            <span className="bg-gradient-to-r from-blue-400 via-indigo-300 to-purple-400 bg-clip-text text-transparent">
              Job Matching Engine
            </span>
          </h1>

          <p className="mt-6 text-base sm:text-lg text-slate-300 leading-relaxed max-w-2xl mx-auto">
            Eliminate traditional keyword filtering. Our multi-stage NLP pipeline measures semantic
            conceptual alignment, extracts verified skills against ontology graphs, and computes
            optimal marketplace allocation.
          </p>

          {/* Dual Call-to-Action */}
          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Button
              asChild
              size="lg"
              className="w-full sm:w-auto h-12 px-7 text-base font-semibold shadow-lg shadow-blue-500/25 group"
            >
              <Link href="/recruiter/candidates">
                <FileCheck2 className="h-5 w-5 mr-2 text-blue-200 group-hover:scale-110 transition-transform" />
                Evaluate Candidate Resume
                <ArrowRight className="h-4 w-4 ml-2 group-hover:translate-x-1 transition-transform" />
              </Link>
            </Button>

            <Button
              asChild
              variant="outline"
              size="lg"
              className="w-full sm:w-auto h-12 px-7 text-base font-semibold border-slate-700 bg-slate-900/60 hover:bg-slate-800"
            >
              <Link href="/recruiter/post-job">
                <Briefcase className="h-5 w-5 mr-2 text-slate-300" />
                Post &amp; Match Job
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Feature Pillar Grid */}
      <section className="py-16 sm:py-20 container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-12">
          <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">
            Architected for High-Fidelity Talent Calibration
          </h2>
          <p className="mt-2 text-sm text-slate-400">
            Engineered with modern algorithms to replace superficial ATS pattern matches with true
            conceptual comprehension.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="border-slate-800/80 bg-slate-900/50 hover:border-blue-500/40 transition-all">
            <CardHeader>
              <div className="h-10 w-10 rounded-lg bg-blue-500/10 flex items-center justify-center text-blue-400 mb-2 border border-blue-500/20">
                <BrainCircuit className="h-5 w-5" />
              </div>
              <CardTitle className="text-lg">Sentence-BERT Embeddings</CardTitle>
              <CardDescription className="text-xs text-slate-400">
                Dense high-dimensional vector representations evaluate contextual engineering depth
                rather than raw string matches.
              </CardDescription>
            </CardHeader>
            <CardContent className="text-xs text-slate-400 space-y-2">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                <span>Cosine similarity scoring across semantic blocks</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                <span>TF-IDF weighted domain keyword calibration</span>
              </div>
            </CardContent>
          </Card>

          <Card className="border-slate-800/80 bg-slate-900/50 hover:border-indigo-500/40 transition-all">
            <CardHeader>
              <div className="h-10 w-10 rounded-lg bg-indigo-500/10 flex items-center justify-center text-indigo-400 mb-2 border border-indigo-500/20">
                <Layers className="h-5 w-5" />
              </div>
              <CardTitle className="text-lg">Taxonomy &amp; Skill Normalization</CardTitle>
              <CardDescription className="text-xs text-slate-400">
                Wagner-Fischer distance algorithms and Trie lookups reconcile messy skill aliases
                into canonical profiles.
              </CardDescription>
            </CardHeader>
            <CardContent className="text-xs text-slate-400 space-y-2">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                <span>Automated alias resolution (e.g. k8s &rarr; Kubernetes)</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                <span>Importance-weighted proficiency radar breakdown</span>
              </div>
            </CardContent>
          </Card>

          <Card className="border-slate-800/80 bg-slate-900/50 hover:border-purple-500/40 transition-all">
            <CardHeader>
              <div className="h-10 w-10 rounded-lg bg-purple-500/10 flex items-center justify-center text-purple-400 mb-2 border border-purple-500/20">
                <Binary className="h-5 w-5" />
              </div>
              <CardTitle className="text-lg">Min-Cost Flow Allocation</CardTitle>
              <CardDescription className="text-xs text-slate-400">
                Global talent optimization via bipartite graph matching ensures team skill coverage
                at minimal overall vacancy cost.
              </CardDescription>
            </CardHeader>
            <CardContent className="text-xs text-slate-400 space-y-2">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                <span>Exact min-cover bitmasking for critical projects</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                <span>Multi-candidate team composition optimization</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Active Roles Preview */}
      <section className="py-12 border-t border-slate-900 bg-slate-950/40">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-8 gap-4">
            <div>
              <h3 className="text-xl font-bold text-white">Active Requisitions</h3>
              <p className="text-xs text-slate-400">
                Target job profiles currently configured in the matching engine
              </p>
            </div>
            <Button asChild variant="outline" size="sm">
              <Link href="/recruiter/post-job">
                <Zap className="h-3.5 w-3.5 mr-1 text-blue-400" />
                Create New Requisition
              </Link>
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {jobs.slice(0, 3).map((job) => (
              <Card
                key={job.id}
                className="border-slate-800 bg-slate-900/60 flex flex-col justify-between"
              >
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <Badge variant="secondary" className="text-[10px] font-mono">
                      {job.department}
                    </Badge>
                    <Badge variant="outline" className="text-[10px]">
                      {job.experienceLevel}
                    </Badge>
                  </div>
                  <CardTitle className="text-base">{job.title}</CardTitle>
                  <CardDescription className="line-clamp-2 text-xs">
                    {job.rawDescription}
                  </CardDescription>
                </CardHeader>

                <CardContent className="pt-0">
                  <div className="flex flex-wrap gap-1.5 mb-4">
                    {job.requiredSkills.slice(0, 4).map((s) => (
                      <span
                        key={s}
                        className="rounded bg-slate-800 px-2 py-0.5 text-[11px] text-slate-300 font-medium"
                      >
                        {s}
                      </span>
                    ))}
                    {job.requiredSkills.length > 4 && (
                      <span className="text-[10px] text-slate-500 self-center">
                        +{job.requiredSkills.length - 4} more
                      </span>
                    )}
                  </div>

                  <Button asChild variant="secondary" size="sm" className="w-full">
                    <Link href={`/recruiter/candidates?jobId=${job.id}`}>
                      Evaluate Against Role &rarr;
                    </Link>
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
