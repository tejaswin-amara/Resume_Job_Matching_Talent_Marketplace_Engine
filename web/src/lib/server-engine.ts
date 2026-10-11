export interface ServerJob {
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

export const INITIAL_JOBS: ServerJob[] = [
  {
    id: "101",
    title: "Senior Full-Stack Engineer",
    department: "Engineering",
    description: "We are seeking a Senior Full-Stack Engineer proficient in Python, FastAPI, and TypeScript with React.",
    requirements: "Proficient in Python, FastAPI, TypeScript, React, Docker, and PostgreSQL.",
    min_experience: 5.0,
    max_experience: 10.0,
    location: "Remote",
    headcount: 2,
    skills: ["Python", "FastAPI", "TypeScript", "React", "PostgreSQL", "Docker"],
  },
  {
    id: "102",
    title: "Lead Machine Learning Engineer",
    department: "AI Research",
    description: "Looking for an NLP / ML Engineer to lead vector search matching engine development with PyTorch and pgvector.",
    requirements: "Proficient in Python, PyTorch, NLP, SentenceTransformers, and pgvector.",
    min_experience: 4.0,
    max_experience: 8.0,
    location: "San Francisco, CA",
    headcount: 1,
    skills: ["Python", "PyTorch", "NLP", "Machine Learning", "pgvector", "SentenceTransformers"],
  },
  {
    id: "103",
    title: "Entry-Level Frontend Developer",
    department: "Product Engineering",
    description: "Great opportunity for junior talent to work on modern React interfaces.",
    requirements: "Proficient in JavaScript, HTML, CSS, React, and Git.",
    min_experience: 0.0,
    max_experience: 2.0,
    location: "New York, NY",
    headcount: 2,
    skills: ["JavaScript", "HTML", "CSS", "React", "Git"],
  },
  {
    id: "104",
    title: "Cloud Infrastructure Lead",
    department: "DevOps",
    description: "Lead DevOps and Cloud infrastructure migration on AWS with Kubernetes and Go microservices.",
    requirements: "Proficient in Kubernetes, AWS, Docker, Go, and Linux.",
    min_experience: 8.0,
    max_experience: 15.0,
    location: "Remote",
    headcount: 1,
    skills: ["Kubernetes", "AWS", "Docker", "Go", "Linux"],
  },
];

export const SKILL_TAXONOMY = [
  "python", "java", "c++", "go", "rust", "javascript", "typescript",
  "react", "angular", "vue", "next.js", "node.js", "django", "flask",
  "fastapi", "spring boot", "aws", "gcp", "azure", "docker", "kubernetes",
  "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
  "kafka", "rabbitmq", "pytorch", "tensorflow", "nlp", "sentencetransformers",
  "pgvector", "machine learning", "html", "css", "tailwind css", "git", "linux"
];

export function extractSkillsFromText(text: string): string[] {
  const lower = text.toLowerCase();
  const matched = new Set<string>();

  for (const skill of SKILL_TAXONOMY) {
    const escaped = skill.replace(/[-/\\^$*+?.()|[\]{}]/g, "\\$&");
    const regex = new RegExp(`\\b${escaped}\\b`, "i");
    if (regex.test(lower) || lower.includes(skill)) {
      // Capitalize for display
      const display = skill
        .split(" ")
        .map(w => w.charAt(0).toUpperCase() + w.slice(1))
        .join(" ");
      matched.add(display);
    }
  }

  if (matched.size === 0) {
    // Default fallback skills if minimal sample text uploaded
    matched.add("Python");
    matched.add("FastAPI");
    matched.add("Docker");
  }

  return Array.from(matched);
}

export function calculateHybridATSScore(
  candText: string,
  candSkills: string[],
  candExp: number,
  candEdu: number,
  job: ServerJob
) {
  const jobText = `${job.title} ${job.description} ${job.requirements}`.toLowerCase();
  const candTextLower = candText.toLowerCase();

  // 1. Semantic score via token Jaccard similarity
  const cTokens = new Set(candTextLower.match(/[\w-]+/g) || []);
  const jTokens = new Set(jobText.match(/[\w-]+/g) || []);
  let semScore = 0.5;
  if (cTokens.size > 0 && jTokens.size > 0) {
    let intersection = 0;
    for (const t of cTokens) {
      if (jTokens.has(t)) intersection++;
    }
    const union = new Set([...cTokens, ...jTokens]).size;
    semScore = Math.min(1.0, Math.max(0.0, (intersection / (union || 1)) * 2.0));
  }

  // 2. Skill match
  const candSet = new Set(candSkills.map(s => s.toLowerCase()));
  const reqSkills = job.skills.map(s => s.toLowerCase());
  const matchedSkills: string[] = [];
  const missingSkills: string[] = [];

  for (const s of job.skills) {
    if (candSet.has(s.toLowerCase()) || candTextLower.includes(s.toLowerCase())) {
      matchedSkills.push(s);
    } else {
      missingSkills.push(s);
    }
  }

  const skillScore = reqSkills.length > 0 ? matchedSkills.length / reqSkills.length : 1.0;

  // 3. Experience alignment
  const expScore = job.min_experience > 0 ? Math.min(1.0, Math.max(0.0, candExp / job.min_experience)) : 1.0;

  // 4. Education fit
  const eduScore = Math.min(1.0, Math.max(0.0, candEdu / 3.0));

  // Weights: 40% semantic, 35% skill, 15% experience, 10% education
  const total = 100 * (0.40 * semScore + 0.35 * skillScore + 0.15 * expScore + 0.10 * eduScore);
  const totalScore = Math.round(total * 100) / 100;

  const suggestions: string[] = [];
  if (missingSkills.length > 0) {
    suggestions.push(`Consider building projects with: ${missingSkills.slice(0, 3).join(", ")}`);
  }
  if (candExp < job.min_experience) {
    suggestions.push(`Highlight open source or freelance projects to bridge the ${job.min_experience} year experience requirement.`);
  }

  return {
    candidate_id: "cand_" + Math.random().toString(36).substring(2, 9),
    job_id: job.id,
    total_score: totalScore,
    semantic_score: Math.round(semScore * 10000) / 10000,
    skill_score: Math.round(skillScore * 10000) / 10000,
    experience_score: Math.round(expScore * 10000) / 10000,
    education_score: Math.round(eduScore * 10000) / 10000,
    matched_skills: matchedSkills,
    missing_skills: missingSkills,
    suggestions,
  };
}
