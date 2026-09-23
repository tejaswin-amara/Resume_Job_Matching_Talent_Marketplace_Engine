import {
  type CandidateEvaluation,
  CandidateEvaluationSchema,
  type CreateJobInput,
  type JobProfile,
  JobProfileSchema,
} from '@/contracts/match-engine.schema';
import { z } from 'zod';

export class ApiClientError extends Error {
  constructor(
    message: string,
    public status = 500,
    public details?: unknown,
  ) {
    super(message);
    this.name = 'ApiClientError';
  }
}

const DEFAULT_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export function isMockEnabled(): boolean {
  // Default to mock when explicitly set to 'true' or in browser dev if backend isn't configured
  if (process.env.NEXT_PUBLIC_USE_MOCK === 'false') {
    return false;
  }
  return true;
}

// In-memory mock store for standalone runs
const MOCK_JOBS: JobProfile[] = [
  {
    id: 'a0000000-0000-4000-8000-000000000001',
    title: 'Senior Fullstack Architect',
    department: 'Platform Engineering',
    experienceLevel: 'Senior',
    rawDescription:
      'Architect and build real-time talent matching platforms using React 19, Next.js, and high-throughput microservices. Requires strong foundations in TypeScript, state modeling, and distributed system integration.',
    requiredSkills: ['React', 'Next.js', 'TypeScript', 'Node.js', 'PostgreSQL', 'Docker'],
  },
  {
    id: 'a0000000-0000-4000-8000-000000000002',
    title: 'Machine Learning & Engine Specialist',
    department: 'Algorithm Research',
    experienceLevel: 'Senior',
    rawDescription:
      'Design, benchmark, and deploy semantic embedding pipelines, TF-IDF feature rankers, and min-cost flow allocation algorithms for resume matching and talent supply optimization.',
    requiredSkills: ['Python', 'FastAPI', 'PyTorch', 'Vector Embeddings', 'Docker'],
  },
  {
    id: 'a0000000-0000-4000-8000-000000000003',
    title: 'Distributed Systems & Backend Engineer',
    department: 'Core Infrastructure',
    experienceLevel: 'Mid-Level',
    rawDescription:
      'Develop resilient enterprise matching services with high concurrent query throughput. Lead Kafka streaming consumers and Redis caching topologies.',
    requiredSkills: ['Java', 'Spring Boot', 'PostgreSQL', 'Redis', 'Kafka'],
  },
];

const MOCK_EVALUATIONS: Record<string, CandidateEvaluation> = {
  'e0000000-0000-4000-8000-000000000001': {
    candidateId: 'e0000000-0000-4000-8000-000000000001',
    name: 'Elena Rostova',
    email: 'elena.rostova@engineer.dev',
    parsedAt: new Date().toISOString(),
    matchMetrics: {
      overallScore: 88,
      semanticSimilarity: 92,
      keywordDensityScore: 81,
      experienceMatchScore: 90,
      sharedSkills: ['React', 'Next.js', 'TypeScript', 'Node.js', 'PostgreSQL'],
      missingCoreSkills: ['Docker', 'Kubernetes'],
      skillAssessments: [
        {
          skill: 'React / Next.js',
          importanceWeight: 0.95,
          candidateProficiency: 96,
          match: true,
        },
        {
          skill: 'TypeScript',
          importanceWeight: 0.9,
          candidateProficiency: 92,
          match: true,
        },
        {
          skill: 'Node.js',
          importanceWeight: 0.85,
          candidateProficiency: 88,
          match: true,
        },
        {
          skill: 'PostgreSQL',
          importanceWeight: 0.8,
          candidateProficiency: 82,
          match: true,
        },
        {
          skill: 'System Architecture',
          importanceWeight: 0.85,
          candidateProficiency: 85,
          match: true,
        },
        {
          skill: 'Docker / DevOps',
          importanceWeight: 0.75,
          candidateProficiency: 45,
          match: false,
        },
      ],
      llmFeedback: {
        summary:
          'Candidate exhibits outstanding frontend architecture depth and proficient fullstack TypeScript capabilities. Semantic embeddings reflect 92% alignment with Senior Platform requirements. Minor containerization gaps can be addressed during onboarding.',
        strengths: [
          'Extensive production Next.js App Router and server state optimization experience',
          'Demonstrated expertise in resilient client-side schema validation and responsive UI systems',
          'Strong data modeling discipline with relational databases',
        ],
        interviewQuestions: [
          'How have you previously managed complex server/client state invalidation in Next.js applications?',
          'Describe how you would design a zero-latency resume embedding cache in Redis.',
          'Walk through your strategy for mitigating container cold starts in containerized frontend deployments.',
        ],
      },
    },
  },
};

function generateMockEvaluation(fileName: string, targetJob?: JobProfile): CandidateEvaluation {
  const baseSkills = targetJob?.requiredSkills || [
    'React',
    'Next.js',
    'TypeScript',
    'PostgreSQL',
    'Docker',
  ];

  const candidateId = `e${Math.random().toString(36).substring(2, 9).padEnd(7, '0')}-0000-4000-8000-000000000000`;
  const cleanName = fileName
    .replace(/\.[^/.]+$/, '')
    .replace(/[_-]/g, ' ')
    .replace(/\b\w/g, (l) => l.toUpperCase());

  const assessments = baseSkills.map((skill, index) => {
    // Determine proficiency pseudo-deterministically
    const prof = 70 + ((index * 13 + fileName.length) % 28);
    const weight = Math.round((0.7 + (index % 3) * 0.1) * 100) / 100;
    return {
      skill,
      importanceWeight: weight,
      candidateProficiency: Math.min(100, prof),
      match: prof >= 65,
    };
  });

  const shared = assessments.filter((a) => a.match).map((a) => a.skill);
  const missing = assessments.filter((a) => !a.match).map((a) => a.skill);
  if (missing.length === 0 && assessments.length > 2) {
    missing.push('Kubernetes Cluster Ops');
  }

  const overall = Math.round(
    assessments.reduce((acc, curr) => acc + curr.candidateProficiency, 0) / assessments.length,
  );

  const evaluation: CandidateEvaluation = {
    candidateId,
    name: cleanName || 'Alex Mercer',
    email: `${cleanName.toLowerCase().replace(/\s+/g, '.') || 'alex.mercer'}@example.com`,
    parsedAt: new Date().toISOString(),
    matchMetrics: {
      overallScore: Math.min(98, Math.max(45, overall)),
      semanticSimilarity: Math.min(99, overall + 3),
      keywordDensityScore: Math.max(50, overall - 4),
      experienceMatchScore: Math.min(95, overall + 1),
      sharedSkills: shared,
      missingCoreSkills: missing,
      skillAssessments: assessments,
      llmFeedback: {
        summary: `Automated semantic parsing completed for ${fileName}. Vector similarity matches ${overall}% of the target role taxonomy.`,
        strengths: [
          `Strong proficiency evidenced in ${shared.slice(0, 3).join(', ')}`,
          'Structured work history aligning with the target seniority profile',
          'Clean technical artifact cadence across production repositories',
        ],
        interviewQuestions: [
          `Can you walk through your deepest architectural challenge using ${shared[0] || 'modern web stacks'}?`,
          `How would you quickly close knowledge gaps in ${missing[0] || 'advanced distributed messaging'}?`,
          'Describe a time when you had to trade off strict data consistency for write availability.',
        ],
      },
    },
  };

  // Validate via Zod to guarantee schema contract adherence
  return CandidateEvaluationSchema.parse(evaluation);
}

export const apiClient = {
  isMock: isMockEnabled,

  async getJobs(): Promise<JobProfile[]> {
    if (isMockEnabled()) {
      return [...MOCK_JOBS];
    }

    const response = await fetch(`${DEFAULT_BASE_URL}/api/v1/jobs`, {
      headers: { Accept: 'application/json' },
    });

    if (!response.ok) {
      throw new ApiClientError(`Failed to fetch jobs: ${response.statusText}`, response.status);
    }

    const data = await response.json();
    return z.array(JobProfileSchema).parse(data);
  },

  async createJob(jobInput: CreateJobInput): Promise<JobProfile> {
    const validated = JobProfileSchema.omit({ id: true }).parse(jobInput);

    if (isMockEnabled()) {
      const newJob: JobProfile = {
        id: `a${Math.random().toString(36).substring(2, 9).padEnd(7, '0')}-0000-4000-8000-000000000000`,
        ...validated,
      };
      MOCK_JOBS.unshift(newJob);
      return JobProfileSchema.parse(newJob);
    }

    const response = await fetch(`${DEFAULT_BASE_URL}/api/v1/jobs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify(validated),
    });

    if (!response.ok) {
      const errText = await response.text();
      throw new ApiClientError(
        `Failed to create job: ${errText || response.statusText}`,
        response.status,
      );
    }

    const data = await response.json();
    return JobProfileSchema.parse(data);
  },

  async evaluateResume(file: File, jobId?: string): Promise<CandidateEvaluation> {
    if (isMockEnabled()) {
      // Simulate realistic network latency
      await new Promise((resolve) => setTimeout(resolve, 800));
      const targetJob = MOCK_JOBS.find((j) => j.id === jobId) || MOCK_JOBS[0];
      const evaluation = generateMockEvaluation(file.name, targetJob);
      MOCK_EVALUATIONS[evaluation.candidateId] = evaluation;
      return evaluation;
    }

    const formData = new FormData();
    formData.append('resume', file);
    if (jobId) {
      formData.append('jobId', jobId);
    }

    const response = await fetch(`${DEFAULT_BASE_URL}/api/v1/resumes/evaluate`, {
      method: 'POST',
      headers: {
        Accept: 'application/json',
      },
      body: formData,
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => null);
      throw new ApiClientError(
        errData?.message || `Resume evaluation failed: ${response.statusText}`,
        response.status,
        errData,
      );
    }

    const data = await response.json();
    return CandidateEvaluationSchema.parse(data);
  },

  async getEvaluation(candidateId: string): Promise<CandidateEvaluation> {
    if (isMockEnabled()) {
      const evaluation = MOCK_EVALUATIONS[candidateId];
      if (!evaluation) {
        throw new ApiClientError('Candidate evaluation not found', 404);
      }
      return evaluation;
    }

    const response = await fetch(
      `${DEFAULT_BASE_URL}/api/v1/candidates/${candidateId}/evaluation`,
      {
        headers: { Accept: 'application/json' },
      },
    );

    if (!response.ok) {
      throw new ApiClientError(
        `Candidate evaluation not found: ${response.statusText}`,
        response.status,
      );
    }

    const data = await response.json();
    return CandidateEvaluationSchema.parse(data);
  },
};
