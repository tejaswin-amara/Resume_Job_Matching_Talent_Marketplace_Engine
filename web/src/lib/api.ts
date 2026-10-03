const API_BASE = '/api/v1';

export interface Job {
  id: string;
  title: string;
  department: string;
  description: string;
  requirements: string[];
  experienceRange: string;
  skills: string[];
}

export interface ParsedResume {
  skills: string[];
  experience: any[];
  education: any[];
  rawText: string;
}

export interface MatchScore {
  candidateId: string;
  candidateName?: string;
  overallScore: number;
  semanticScore: number;
  skillScore: number;
  experienceScore: number;
  educationScore: number;
  skillGaps: string[];
  matchedSkills: string[];
}

export const api = {
  uploadResume: async (file: File): Promise<any> => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/resumes/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) throw new Error('Upload failed');
    return res.json();
  },
  parseText: async (text: string): Promise<ParsedResume> => {
    const res = await fetch(`${API_BASE}/resumes/parse-text`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });
    if (!res.ok) throw new Error('Parsing failed');
    return res.json();
  },
  createJob: async (job: Omit<Job, 'id'>): Promise<Job> => {
    const res = await fetch(`${API_BASE}/jobs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(job),
    });
    if (!res.ok) throw new Error('Job creation failed');
    return res.json();
  },
  getJobs: async (): Promise<{items: Job[], total: number}> => {
    const res = await fetch(`${API_BASE}/jobs`);
    if (!res.ok) throw new Error('Failed to fetch jobs');
    return res.json();
  },
  getJobMatches: async (jobId: string): Promise<MatchScore[]> => {
    const res = await fetch(`${API_BASE}/jobs/${jobId}/matches`);
    if (!res.ok) throw new Error('Failed to fetch matches');
    return res.json();
  },
  adhocMatch: async (resumeText: string, jobDescription: string): Promise<MatchScore> => {
    const res = await fetch(`${API_BASE}/match/adhoc`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ resumeText, jobDescription }),
    });
    if (!res.ok) throw new Error('Adhoc match failed');
    return res.json();
  },
  allocateMarketplace: async (): Promise<any> => {
    const res = await fetch(`${API_BASE}/marketplace/allocate`, { method: 'POST' });
    if (!res.ok) throw new Error('Allocation failed');
    return res.json();
  },
  getBottlenecks: async (): Promise<any> => {
    const res = await fetch(`${API_BASE}/marketplace/bottlenecks`, { method: 'POST' });
    if (!res.ok) throw new Error('Bottleneck analysis failed');
    return res.json();
  },
  buildTeam: async (req: any): Promise<any> => {
    const res = await fetch(`${API_BASE}/marketplace/team-builder`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req),
    });
    if (!res.ok) throw new Error('Team builder failed');
    return res.json();
  }
};
