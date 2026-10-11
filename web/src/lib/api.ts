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

const AUTH_HEADERS = {
  Authorization: 'Bearer demo-token',
};

export const api = {
  uploadResume: async (file: File): Promise<any> => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/resumes/upload`, {
      method: 'POST',
      headers: {
        ...AUTH_HEADERS,
      },
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(err.detail || err.title || 'Upload failed');
    }
    const data = await res.json();
    return {
      ...data,
      skills: data.skills || data.parsed_skills || data.skills_extracted || [],
    };
  },
  parseText: async (text: string): Promise<ParsedResume> => {
    const res = await fetch(`${API_BASE}/resumes/parse-text`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...AUTH_HEADERS,
      },
      body: JSON.stringify({ text }),
    });
    if (!res.ok) throw new Error('Parsing failed');
    const data = await res.json();
    return {
      ...data,
      skills: data.skills || data.parsed_skills || data.skills_extracted || [],
    };
  },
  createJob: async (job: Omit<Job, 'id'>): Promise<Job> => {
    const res = await fetch(`${API_BASE}/jobs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...AUTH_HEADERS,
      },
      body: JSON.stringify(job),
    });
    if (!res.ok) throw new Error('Job creation failed');
    return res.json();
  },
  getJobs: async (): Promise<Job[]> => {
    const res = await fetch(`${API_BASE}/jobs`, {
      headers: {
        ...AUTH_HEADERS,
      },
    });
    if (!res.ok) throw new Error('Failed to fetch jobs');
    const data = await res.json();
    return Array.isArray(data) ? data : data.items || [];
  },
  getJobMatches: async (jobId: string): Promise<MatchScore[]> => {
    const res = await fetch(`${API_BASE}/jobs/${jobId}/matches`, {
      headers: {
        ...AUTH_HEADERS,
      },
    });
    if (!res.ok) throw new Error('Failed to fetch matches');
    const data = await res.json();
    return Array.isArray(data) ? data : data.matches || [];
  },
  adhocMatch: async (resume_text: string, job_description: string): Promise<MatchScore> => {
    const res = await fetch(`${API_BASE}/match/adhoc`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...AUTH_HEADERS,
      },
      body: JSON.stringify({ resume_text, job_description }),
    });
    if (!res.ok) throw new Error('Adhoc match failed');
    const data = await res.json();
    return data.match_result || data;
  },
  allocateMarketplace: async (): Promise<any> => {
    const res = await fetch(`${API_BASE}/marketplace/allocate`, {
      method: 'POST',
      headers: {
        ...AUTH_HEADERS,
      },
    });
    if (!res.ok) throw new Error('Allocation failed');
    return res.json();
  },
  getBottlenecks: async (): Promise<any> => {
    const res = await fetch(`${API_BASE}/marketplace/bottlenecks`, {
      method: 'POST',
      headers: {
        ...AUTH_HEADERS,
      },
    });
    if (!res.ok) throw new Error('Bottleneck analysis failed');
    return res.json();
  },
  buildTeam: async (req: any): Promise<any> => {
    const res = await fetch(`${API_BASE}/marketplace/team-builder`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...AUTH_HEADERS,
      },
      body: JSON.stringify(req),
    });
    if (!res.ok) throw new Error('Team builder failed');
    return res.json();
  },
};
