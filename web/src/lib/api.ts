const API_BASE = '/api/v1';

export interface Job {
  id: string;
  title: string;
  department: string;
  description: string;
  requirements: string;
  min_experience: number;
  max_experience?: number;
  location?: string;
  headcount: number;
  skills: string[];
}

export interface ParsedResume {
  skills: string[];
  raw_text?: string;
}

export interface MatchScore {
  candidate_id: string;
  job_id: string;
  total_score: number;
  semantic_score: number;
  skill_score: number;
  experience_score: number;
  education_score: number;
  matched_skills: string[];
  missing_skills: string[];
  suggestions: string[];
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
    // FIXED: send text in body, not url param
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
  getJobs: async (): Promise<Job[]> => {
    const res = await fetch(`${API_BASE}/jobs`);
    if (!res.ok) throw new Error('Failed to fetch jobs');
    return res.json();
  },
  getJobMatches: async (jobId: string): Promise<MatchScore[]> => {
    const res = await fetch(`${API_BASE}/jobs/${jobId}/matches`);
    if (!res.ok) throw new Error('Failed to fetch matches');
    return res.json();
  },
  adhocMatch: async (resume_text: string, job_description: string): Promise<MatchScore> => {
    const res = await fetch(`${API_BASE}/match/adhoc`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ resume_text, job_description }),
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
