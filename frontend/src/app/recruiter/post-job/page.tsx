'use client';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  type CreateJobInput,
  CreateJobInputSchema,
  ExperienceLevelSchema,
} from '@/contracts/match-engine.schema';
import { apiClient } from '@/lib/api-client';
import { zodResolver } from '@hookform/resolvers/zod';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { AlertCircle, Briefcase, CheckCircle2, Plus, Sliders, Sparkles, X } from 'lucide-react';
import { useRouter } from 'next/navigation';
import * as React from 'react';
import { useForm } from 'react-hook-form';

type SkillImportance = 'Critical' | 'Desirable' | 'Optional';

interface ConfiguredSkill {
  name: string;
  importance: SkillImportance;
  weight: number;
}

const IMPORTANCE_CONFIG: Record<SkillImportance, { weight: number; colorClass: string }> = {
  Critical: { weight: 1.0, colorClass: 'border-rose-700/60 bg-rose-950/40 text-rose-300' },
  Desirable: { weight: 0.7, colorClass: 'border-blue-700/60 bg-blue-950/40 text-blue-300' },
  Optional: { weight: 0.4, colorClass: 'border-slate-700 bg-slate-800 text-slate-300' },
};

export default function PostJobPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [skills, setSkills] = React.useState<ConfiguredSkill[]>([
    { name: 'React', importance: 'Critical', weight: 1.0 },
    { name: 'TypeScript', importance: 'Critical', weight: 1.0 },
    { name: 'Next.js', importance: 'Desirable', weight: 0.7 },
    { name: 'Docker', importance: 'Optional', weight: 0.4 },
  ]);
  const [newSkillText, setNewSkillText] = React.useState('');
  const [newSkillImportance, setNewSkillImportance] = React.useState<SkillImportance>('Critical');
  const [skillError, setSkillError] = React.useState<string | null>(null);

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<CreateJobInput>({
    resolver: zodResolver(CreateJobInputSchema),
    defaultValues: {
      title: '',
      department: '',
      experienceLevel: 'Senior',
      rawDescription: '',
      requiredSkills: ['React', 'TypeScript', 'Next.js', 'Docker'],
    },
  });

  const syncSkillsToForm = (updatedSkills: ConfiguredSkill[]) => {
    setSkills(updatedSkills);
    const skillNames = updatedSkills.map((s) => s.name);
    setValue('requiredSkills', skillNames, { shouldValidate: true });
  };

  const handleAddSkill = (e: React.FormEvent) => {
    e.preventDefault();
    const clean = newSkillText.trim();
    if (!clean) return;

    if (skills.some((s) => s.name.toLowerCase() === clean.toLowerCase())) {
      setSkillError('This skill has already been specified');
      return;
    }

    setSkillError(null);
    const updated = [
      ...skills,
      {
        name: clean,
        importance: newSkillImportance,
        weight: IMPORTANCE_CONFIG[newSkillImportance].weight,
      },
    ];
    syncSkillsToForm(updated);
    setNewSkillText('');
  };

  const handleRemoveSkill = (skillName: string) => {
    const updated = skills.filter((s) => s.name !== skillName);
    syncSkillsToForm(updated);
  };

  const handleCycleImportance = (skillName: string) => {
    const sequence: SkillImportance[] = ['Critical', 'Desirable', 'Optional'];
    const updated = skills.map((s) => {
      if (s.name !== skillName) return s;
      const currentIndex = sequence.indexOf(s.importance);
      const nextImportance = sequence[(currentIndex + 1) % sequence.length];
      return {
        ...s,
        importance: nextImportance,
        weight: IMPORTANCE_CONFIG[nextImportance].weight,
      };
    });
    syncSkillsToForm(updated);
  };

  const createJobMutation = useMutation({
    mutationFn: (data: CreateJobInput) => apiClient.createJob(data),
    onSuccess: (newJob) => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
      router.push(`/recruiter/candidates?jobId=${newJob.id}`);
    },
  });

  const onSubmit = (data: CreateJobInput) => {
    createJobMutation.mutate(data);
  };

  return (
    <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-10 max-w-3xl">
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-xs font-semibold uppercase tracking-wider text-blue-400">
            Requisition Architecture
          </span>
          <Badge variant="outline" className="text-[10px] border-blue-500/30 text-blue-300">
            Ontology Config
          </Badge>
        </div>
        <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
          Post &amp; Configure Target Role
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Create an AI-evaluated job requisition with importance-weighted competency criteria.
        </p>
      </div>

      <Card className="border-slate-800 bg-slate-900/60">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Briefcase className="h-5 w-5 text-blue-400" />
            Job Profile Specification
          </CardTitle>
          <CardDescription className="text-xs">
            Uncontrolled schema form validated via Zod DTO contracts
          </CardDescription>
        </CardHeader>

        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Title & Department */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="title">Job Title *</Label>
                <Input
                  id="title"
                  placeholder="e.g. Senior Fullstack Architect"
                  {...register('title')}
                  className={errors.title ? 'border-rose-500' : ''}
                />
                {errors.title && (
                  <p className="text-xs text-rose-400 flex items-center gap-1">
                    <AlertCircle className="h-3 w-3" />
                    {errors.title.message}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="department">Department / Team *</Label>
                <Input
                  id="department"
                  placeholder="e.g. Platform Engineering"
                  {...register('department')}
                  className={errors.department ? 'border-rose-500' : ''}
                />
                {errors.department && (
                  <p className="text-xs text-rose-400 flex items-center gap-1">
                    <AlertCircle className="h-3 w-3" />
                    {errors.department.message}
                  </p>
                )}
              </div>
            </div>

            {/* Experience Level */}
            <div className="space-y-2">
              <Label htmlFor="experienceLevel">Target Seniority / Experience Level *</Label>
              <select
                id="experienceLevel"
                {...register('experienceLevel')}
                className="flex h-10 w-full rounded-lg border border-slate-700 bg-slate-900/80 px-3 py-2 text-sm text-slate-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
              >
                {ExperienceLevelSchema.options.map((lvl) => (
                  <option key={lvl} value={lvl}>
                    {lvl} Level
                  </option>
                ))}
              </select>
            </div>

            {/* Raw Description */}
            <div className="space-y-2">
              <Label htmlFor="rawDescription">Raw Job Description &amp; Responsibilities *</Label>
              <Textarea
                id="rawDescription"
                rows={5}
                placeholder="Describe role objectives, technical expectations, architecture scope..."
                {...register('rawDescription')}
                className={errors.rawDescription ? 'border-rose-500' : ''}
              />
              {errors.rawDescription && (
                <p className="text-xs text-rose-400 flex items-center gap-1">
                  <AlertCircle className="h-3 w-3" />
                  {errors.rawDescription.message}
                </p>
              )}
            </div>

            {/* Dynamic Skill Tags with Importance Levels */}
            <div className="space-y-3 pt-2 border-t border-slate-800">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-sm font-semibold text-white flex items-center gap-1.5">
                    <Sliders className="h-4 w-4 text-blue-400" />
                    Required Skills &amp; Importance Sliders
                  </Label>
                  <p className="text-xs text-slate-400">
                    Click any badge to cycle its weight (Critical &rarr; Desirable &rarr; Optional)
                  </p>
                </div>
                <span className="text-xs text-slate-400 font-mono">{skills.length} configured</span>
              </div>

              {/* Tag Input Form */}
              <div className="flex gap-2">
                <Input
                  value={newSkillText}
                  onChange={(e) => setNewSkillText(e.target.value)}
                  placeholder="Type skill name (e.g. Kubernetes, PyTorch)..."
                  className="flex-1"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      handleAddSkill(e);
                    }
                  }}
                />
                <select
                  value={newSkillImportance}
                  onChange={(e) => setNewSkillImportance(e.target.value as SkillImportance)}
                  className="h-10 rounded-lg border border-slate-700 bg-slate-900 px-3 text-xs text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="Critical">Critical (1.0x)</option>
                  <option value="Desirable">Desirable (0.7x)</option>
                  <option value="Optional">Optional (0.4x)</option>
                </select>
                <Button
                  type="button"
                  variant="secondary"
                  onClick={handleAddSkill}
                  className="shrink-0"
                >
                  <Plus className="h-4 w-4 mr-1" /> Add
                </Button>
              </div>

              {skillError && (
                <p className="text-xs text-amber-400 flex items-center gap-1">
                  <AlertCircle className="h-3 w-3" />
                  {skillError}
                </p>
              )}

              {/* Tags Cloud */}
              <div className="flex flex-wrap gap-2 pt-2 min-h-[50px] p-3 rounded-lg border border-slate-800/80 bg-slate-950/40">
                {skills.map((skill) => {
                  const cfg = IMPORTANCE_CONFIG[skill.importance];
                  return (
                    <span
                      key={skill.name}
                      className={`inline-flex items-center gap-1.5 rounded-lg border pl-2.5 pr-1.5 py-0.5 text-xs font-medium transition-transform select-none ${cfg.colorClass}`}
                    >
                      <button
                        type="button"
                        onClick={() => handleCycleImportance(skill.name)}
                        className="flex items-center gap-1 cursor-pointer hover:underline text-left"
                        title="Click to cycle importance weight"
                      >
                        <span>{skill.name}</span>
                        <span className="text-[10px] opacity-75 font-mono">
                          ({skill.importance})
                        </span>
                      </button>
                      <button
                        type="button"
                        onClick={() => handleRemoveSkill(skill.name)}
                        className="rounded p-0.5 text-slate-400 hover:text-white hover:bg-slate-800/80 cursor-pointer"
                        aria-label={`Remove ${skill.name}`}
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </span>
                  );
                })}
              </div>

              {errors.requiredSkills && (
                <p className="text-xs text-rose-400 flex items-center gap-1">
                  <AlertCircle className="h-3 w-3" />
                  {errors.requiredSkills.message}
                </p>
              )}
            </div>

            {/* Submit Action */}
            <div className="pt-4 border-t border-slate-800 flex items-center justify-end gap-3">
              <Button
                type="button"
                variant="ghost"
                onClick={() => router.push('/recruiter/candidates')}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                size="lg"
                disabled={isSubmitting || createJobMutation.isPending}
                className="shadow-lg shadow-blue-500/20"
              >
                {createJobMutation.isPending ? (
                  <>Calibrating Requisition...</>
                ) : (
                  <>
                    <Sparkles className="h-4 w-4 mr-2" />
                    Publish &amp; Launch Matching Engine
                  </>
                )}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
