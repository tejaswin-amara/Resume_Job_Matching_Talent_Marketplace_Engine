import { z } from 'zod';

export const ExperienceLevelSchema = z.enum(['Entry', 'Mid-Level', 'Senior', 'Lead', 'Executive']);
export type ExperienceLevel = z.infer<typeof ExperienceLevelSchema>;

export const JobProfileSchema = z.object({
  id: z.string().uuid('Job ID must be a valid UUID'),
  title: z.string().min(1, 'Job title is required'),
  department: z.string().min(1, 'Department is required'),
  experienceLevel: ExperienceLevelSchema,
  rawDescription: z.string().min(1, 'Job description is required'),
  requiredSkills: z.array(z.string().min(1)).min(1, 'At least one skill is required'),
});
export type JobProfile = z.infer<typeof JobProfileSchema>;

export const SkillAssessmentSchema = z.object({
  skill: z.string().min(1, 'Skill name is required'),
  importanceWeight: z
    .number()
    .min(0, 'Weight must be at least 0')
    .max(1, 'Weight must not exceed 1'),
  candidateProficiency: z
    .number()
    .min(0, 'Proficiency must be at least 0')
    .max(100, 'Proficiency must not exceed 100'),
  match: z.boolean(),
});
export type SkillAssessment = z.infer<typeof SkillAssessmentSchema>;

export const LLMFeedbackSchema = z.object({
  summary: z.string().min(1, 'Feedback summary is required'),
  strengths: z.array(z.string()),
  interviewQuestions: z.array(z.string()),
});
export type LLMFeedback = z.infer<typeof LLMFeedbackSchema>;

export const MatchMetricSchema = z.object({
  overallScore: z.number().min(0, 'Score must be at least 0').max(100, 'Score cannot exceed 100'),
  semanticSimilarity: z
    .number()
    .min(0, 'Similarity must be at least 0')
    .max(100, 'Similarity cannot exceed 100'),
  keywordDensityScore: z
    .number()
    .min(0, 'Keyword score must be at least 0')
    .max(100, 'Keyword score cannot exceed 100'),
  experienceMatchScore: z
    .number()
    .min(0, 'Experience match score must be at least 0')
    .max(100, 'Experience match score cannot exceed 100'),
  missingCoreSkills: z.array(z.string()),
  sharedSkills: z.array(z.string()),
  skillAssessments: z.array(SkillAssessmentSchema),
  llmFeedback: LLMFeedbackSchema,
});
export type MatchMetric = z.infer<typeof MatchMetricSchema>;

export const CandidateEvaluationSchema = z.object({
  candidateId: z.string().uuid('Candidate ID must be a valid UUID'),
  name: z.string().min(1, 'Candidate name is required'),
  email: z.string().email('Invalid candidate email address'),
  matchMetrics: MatchMetricSchema,
  parsedAt: z.string().refine((val) => !Number.isNaN(Date.parse(val)), {
    message: 'parsedAt must be a valid ISO timestamp',
  }),
});
export type CandidateEvaluation = z.infer<typeof CandidateEvaluationSchema>;

export const CreateJobInputSchema = JobProfileSchema.omit({ id: true });
export type CreateJobInput = z.infer<typeof CreateJobInputSchema>;
