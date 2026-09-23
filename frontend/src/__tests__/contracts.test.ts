import {
  CandidateEvaluationSchema,
  JobProfileSchema,
  MatchMetricSchema,
  SkillAssessmentSchema,
} from '@/contracts/match-engine.schema';
import { describe, expect, it } from 'vitest';

describe('Match Engine Zod Schema Contract Verification', () => {
  const validJob = {
    id: 'a1234567-89ab-4cde-8f01-23456789abcd',
    title: 'Senior Fullstack Architect',
    department: 'Platform Engineering',
    experienceLevel: 'Senior',
    rawDescription: 'Building resilient modern matching platforms.',
    requiredSkills: ['React', 'Next.js', 'TypeScript', 'Docker'],
  };

  const validEvaluation = {
    candidateId: 'b1234567-89ab-4cde-8f01-23456789abcd',
    name: 'Sarah Connor',
    email: 'sarah.connor@sky.net',
    parsedAt: '2026-03-15T14:30:00.000Z',
    matchMetrics: {
      overallScore: 85,
      semanticSimilarity: 88,
      keywordDensityScore: 82,
      experienceMatchScore: 89,
      sharedSkills: ['React', 'TypeScript'],
      missingCoreSkills: ['Docker'],
      skillAssessments: [
        {
          skill: 'React',
          importanceWeight: 0.9,
          candidateProficiency: 95,
          match: true,
        },
      ],
      llmFeedback: {
        summary: 'Exceptional fullstack expertise demonstrated.',
        strengths: ['Strong system design', 'Clean component hierarchy'],
        interviewQuestions: ['Explain React Server Components architecture.'],
      },
    },
  };

  describe('JobProfileSchema', () => {
    it('successfully validates a compliant job profile', () => {
      const parsed = JobProfileSchema.safeParse(validJob);
      expect(parsed.success).toBe(true);
    });

    it('rejects an invalid UUID for job ID', () => {
      const invalid = { ...validJob, id: 'not-a-valid-uuid-1234' };
      const parsed = JobProfileSchema.safeParse(invalid);
      expect(parsed.success).toBe(false);
      if (!parsed.success) {
        expect(parsed.error.issues[0].message).toMatch(/valid UUID/i);
      }
    });

    it('rejects an empty requiredSkills array', () => {
      const invalid = { ...validJob, requiredSkills: [] };
      const parsed = JobProfileSchema.safeParse(invalid);
      expect(parsed.success).toBe(false);
      if (!parsed.success) {
        expect(parsed.error.issues[0].message).toMatch(/At least one skill/i);
      }
    });

    it('rejects an unsupported experience level', () => {
      const invalid = { ...validJob, experienceLevel: 'MasterOfUniverse' };
      const parsed = JobProfileSchema.safeParse(invalid);
      expect(parsed.success).toBe(false);
    });
  });

  describe('SkillAssessmentSchema', () => {
    it('rejects an importance weight greater than 1', () => {
      const invalid = {
        skill: 'React',
        importanceWeight: 1.5,
        candidateProficiency: 90,
        match: true,
      };
      const parsed = SkillAssessmentSchema.safeParse(invalid);
      expect(parsed.success).toBe(false);
    });

    it('rejects a proficiency greater than 100', () => {
      const invalid = {
        skill: 'React',
        importanceWeight: 0.8,
        candidateProficiency: 150,
        match: true,
      };
      const parsed = SkillAssessmentSchema.safeParse(invalid);
      expect(parsed.success).toBe(false);
    });
  });

  describe('MatchMetricSchema', () => {
    it('rejects overallScore out of 0-100 bounds', () => {
      const invalid = {
        ...validEvaluation.matchMetrics,
        overallScore: 105,
      };
      const parsed = MatchMetricSchema.safeParse(invalid);
      expect(parsed.success).toBe(false);
    });

    it('rejects missing LLM feedback fields', () => {
      const invalid = {
        ...validEvaluation.matchMetrics,
        llmFeedback: { summary: 'incomplete' },
      };
      const parsed = MatchMetricSchema.safeParse(invalid);
      expect(parsed.success).toBe(false);
    });
  });

  describe('CandidateEvaluationSchema', () => {
    it('successfully validates a compliant candidate evaluation payload', () => {
      const parsed = CandidateEvaluationSchema.safeParse(validEvaluation);
      expect(parsed.success).toBe(true);
    });

    it('rejects an invalid email format', () => {
      const invalid = { ...validEvaluation, email: 'not-an-email' };
      const parsed = CandidateEvaluationSchema.safeParse(invalid);
      expect(parsed.success).toBe(false);
    });

    it('rejects an invalid timestamp for parsedAt', () => {
      const invalid = { ...validEvaluation, parsedAt: 'not-a-date' };
      const parsed = CandidateEvaluationSchema.safeParse(invalid);
      expect(parsed.success).toBe(false);
    });
  });
});
