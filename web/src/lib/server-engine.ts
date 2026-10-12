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
  "pgvector", "machine learning", "html", "css", "tailwind css", "git", "linux",
  "graphql", "rest", "ci/cd", "pandas", "numpy", "scikit-learn", "terraform"
];

export interface ExtractedRole {
  title: string;
  company?: string;
  duration?: string;
  description?: string;
}

export interface ExtractedEducation {
  degree: string;
  field?: string;
  institution?: string;
  year?: string;
  level: number;
}

export interface ParsedResumeProfile {
  id: string;
  filename?: string;
  name: string;
  email?: string;
  phone?: string;
  location?: string;
  linkedin?: string;
  github?: string;
  skills: string[];
  parsed_skills: string[];
  skills_extracted: string[];
  years_experience: number;
  education_level: number;
  education: ExtractedEducation[];
  roles: ExtractedRole[];
  raw_text: string;
  summary?: string;
}

export const CANONICAL_SKILL_NAMES: Record<string, string> = {
  "fastapi": "FastAPI",
  "typescript": "TypeScript",
  "javascript": "JavaScript",
  "next.js": "Next.js",
  "node.js": "Node.js",
  "postgresql": "PostgreSQL",
  "mongodb": "MongoDB",
  "sentencetransformers": "SentenceTransformers",
  "pgvector": "pgvector",
  "graphql": "GraphQL",
  "ci/cd": "CI/CD",
  "aws": "AWS",
  "gcp": "GCP",
  "sql": "SQL",
  "html": "HTML",
  "css": "CSS",
  "tailwind css": "Tailwind CSS",
  "c++": "C++",
  "pytorch": "PyTorch",
  "mysql": "MySQL",
};

export function extractSkillsFromText(text: string): string[] {
  const lower = text.toLowerCase();
  const matched = new Set<string>();

  for (const skill of SKILL_TAXONOMY) {
    const escaped = skill.replace(/[-/\\^$*+?.()|[\]{}]/g, "\\$&");
    const regex = new RegExp(`\\b${escaped}\\b`, "i");
    if (regex.test(lower) || lower.includes(skill)) {
      const canonical = CANONICAL_SKILL_NAMES[skill.toLowerCase()];
      const display = canonical || skill
        .split(" ")
        .map(w => w.charAt(0).toUpperCase() + w.slice(1))
        .join(" ");
      matched.add(display);
    }
  }

  if (matched.size === 0) {
    matched.add("Python");
    matched.add("FastAPI");
    matched.add("Docker");
  }

  return Array.from(matched);
}

export function extractNameFromText(text: string, filename?: string): string {
  // 1. Direct label pattern: "Name: John Doe" or "Candidate: John Doe"
  const directMatch = text.match(/(?:^|\n)\s*(?:name|candidate(?:\s+name)?)\s*[:\-]\s*([A-Za-z\.\'\- ]{2,40})/i);
  if (directMatch && directMatch[1]) {
    const cleaned = directMatch[1].trim();
    if (cleaned.split(/\s+/).length >= 2 && !/resume|curriculum|email|phone/i.test(cleaned)) {
      return cleaned;
    }
  }

  // 2. Scan top 15 lines
  const lines = text.split(/\r?\n/).map(l => l.trim()).filter(Boolean);
  const skipKeywords = /^(?:resume|curriculum\s+vitae|cv|profile|summary|professional\s+summary|contact|experience|work\s+experience|education|skills|projects|objective|about\s+me|page\s+\d+|personal\s+details)\b/i;

  for (let i = 0; i < Math.min(lines.length, 15); i++) {
    const line = lines[i];
    if (line.includes("@") || /https?:\/\/|www\.|linkedin|github/i.test(line)) continue;
    if (skipKeywords.test(line)) continue;
    if ((line.match(/\d/g) || []).length > 2) continue;
    if (line.length > 50 || line.length < 3) continue;

    const words = line.split(/\s+/);
    if (words.length >= 2 && words.length <= 4) {
      const isCapitalized = words.every(w => /^[A-Z][a-zA-Z\.\'-]*$/.test(w) || /^[A-Z]+$/.test(w));
      if (isCapitalized) {
        return words.map(w => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()).join(" ");
      }
    }
  }

  // 3. Fallback from filename if provided
  if (filename) {
    const base = filename.replace(/\.(pdf|docx|doc|txt|rtf|md)$/i, "");
    const cleaned = base
      .replace(/[_\-+.]/g, " ")
      .replace(/\b(resume|cv|updated|final|v\d+|\d+)\b/gi, "")
      .trim();
    const parts = cleaned.split(/\s+/).filter(Boolean);
    if (parts.length >= 2) {
      return parts.map(p => p.charAt(0).toUpperCase() + p.slice(1).toLowerCase()).join(" ");
    } else if (parts.length === 1 && parts[0].length > 2) {
      return parts[0].charAt(0).toUpperCase() + parts[0].slice(1).toLowerCase();
    }
  }

  return "Candidate Profile";
}

export function extractContactInfo(text: string) {
  const emailMatch = text.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/);
  const email = emailMatch ? emailMatch[0].toLowerCase() : undefined;

  const phoneMatch = text.match(/(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}/);
  const phone = phoneMatch ? phoneMatch[0].trim() : undefined;

  const linkedinMatch = text.match(/(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/([a-zA-Z0-9_-]+)/i);
  const linkedin = linkedinMatch ? `linkedin.com/in/${linkedinMatch[1]}` : undefined;

  const githubMatch = text.match(/(?:https?:\/\/)?(?:www\.)?github\.com\/([a-zA-Z0-9_-]+)/i);
  const github = githubMatch ? `github.com/${githubMatch[1]}` : undefined;

  let location: string | undefined = undefined;
  const locExplicit = text.match(/(?:location|address|residence)\s*[:\-]\s*([A-Za-z\s]+(?:,\s*[A-Za-z\s]+)?)/i);
  if (locExplicit) {
    location = locExplicit[1].trim();
  } else {
    const cityStateMatch = text.match(/\b([A-Z][a-zA-Z\s]+,\s*(?:[A-Z]{2}|California|New York|Texas|Washington|Remote|London|UK|Canada|Germany|India|Australia))\b/);
    if (cityStateMatch) {
      location = cityStateMatch[1].trim();
    }
  }

  return { email, phone, linkedin, github, location };
}

export function extractEducation(text: string): { education: ExtractedEducation[]; education_level: number } {
  const educationList: ExtractedEducation[] = [];
  const lines = text.split(/\r?\n/);

  const degreePatterns = [
    { regex: /\b(?:ph\.?d|doctorate|doctor of philosophy)\b/i, degree: "Ph.D.", level: 4 },
    { regex: /\b(?:m\.?s\.?|master(?:'s)?(?:\s+of\s+(?:science|arts|engineering|business|administration))?|msc|mba|m\.tech|mtech)\b/i, degree: "Master's Degree", level: 3 },
    { regex: /\b(?:b\.?s\.?|bachelor(?:'s)?(?:\s+of\s+(?:science|arts|engineering))?|bsc|ba|b\.tech|btech|b\.e\.|undergraduate)\b/i, degree: "Bachelor's Degree", level: 2 },
    { regex: /\b(?:associate(?:'s)?|diploma|bootcamp)\b/i, degree: "Associate / Diploma", level: 1 },
  ];

  const uniRegex = /([A-Z][A-Za-z0-9&\'\.\s]+(?:University|College|Institute|Academy|Polytechnic)(?:\s+of\s+[A-Za-z\s]+)?)/;
  const fieldRegex = /(?:in\s+)?(Computer Science|Software Engineering|Data Science|Electrical Engineering|Information Technology|Computer Engineering|Mathematics|Physics|Economics|Business Administration|Artificial Intelligence|Cybersecurity)/i;
  const yearRegex = /\b(19\d{2}|20\d{2})\b/;

  let maxLevel = 2;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    for (const dp of degreePatterns) {
      if (dp.regex.test(line)) {
        if (dp.level > maxLevel) maxLevel = dp.level;

        const context = lines.slice(Math.max(0, i - 1), Math.min(lines.length, i + 3)).join(" ");
        const uniMatch = context.match(uniRegex);
        const fieldMatch = context.match(fieldRegex);
        const yearMatch = context.match(yearRegex);

        let institution = uniMatch ? uniMatch[1].trim() : undefined;
        if (institution) {
          institution = institution.replace(/^(?:education|academic\s+background|bachelor(?:'s)?(?:\s+of\s+[\w\s]+)?|master(?:'s)?(?:\s+of\s+[\w\s]+)?|ph\.?d|in\s+[\w\s]+)\s+/i, "").trim();
        }

        const eduItem: ExtractedEducation = {
          degree: dp.degree,
          level: dp.level,
          institution,
          field: fieldMatch ? fieldMatch[1].trim() : undefined,
          year: yearMatch ? yearMatch[1] : undefined,
        };

        if (!educationList.some(e => e.degree === eduItem.degree && e.institution === eduItem.institution)) {
          educationList.push(eduItem);
        }
        break;
      }
    }
  }

  if (educationList.length === 0) {
    const generalUni = text.match(uniRegex);
    if (generalUni) {
      const yearMatch = text.match(yearRegex);
      educationList.push({
        degree: "Bachelor's Degree",
        institution: generalUni[1].trim(),
        year: yearMatch ? yearMatch[1] : undefined,
        level: 2,
      });
      maxLevel = 2;
    }
  }

  return { education: educationList, education_level: maxLevel };
}

export function extractRolesAndExperience(text: string): { roles: ExtractedRole[]; years_experience: number } {
  const roles: ExtractedRole[] = [];

  // Isolate Experience section if explicit section header exists
  let targetText = text;
  const expHeaderMatch = text.match(/(?:^|\n)\s*(?:work\s+experience|professional\s+experience|employment\s+history|experience)\s*[:\n\r]/i);
  if (expHeaderMatch && expHeaderMatch.index !== undefined) {
    const afterExp = text.slice(expHeaderMatch.index + expHeaderMatch[0].length);
    const nextSectionMatch = afterExp.match(/(?:^|\n)\s*(?:education|academic\s+background|skills|technical\s+skills|projects|certifications|awards|publications)\s*[:\n\r]/i);
    if (nextSectionMatch && nextSectionMatch.index !== undefined) {
      targetText = afterExp.slice(0, nextSectionMatch.index);
    } else {
      targetText = afterExp;
    }
  }

  const lines = targetText.split(/\r?\n/).map(l => l.trim()).filter(Boolean);

  const titlePatterns = [
    "Senior Full-Stack Engineer", "Full-Stack Engineer", "Lead Machine Learning Engineer",
    "Machine Learning Engineer", "Senior Software Engineer", "Software Engineer",
    "Frontend Developer", "Frontend Engineer", "Backend Developer", "Backend Engineer",
    "Cloud Infrastructure Lead", "DevOps Engineer", "Site Reliability Engineer",
    "Data Scientist", "Data Engineer", "Solutions Architect", "Technical Lead",
    "Engineering Manager", "Systems Engineer", "Mobile Developer", "iOS Developer",
    "Android Developer", "QA Engineer", "Full Stack Developer", "Software Developer",
    "Machine Learning Researcher", "Research Scientist", "Product Manager"
  ];

  const dateRangeRegex = /(?:(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*)?(\d{4})\s*[-–—to]+\s*(Present|Current|Now|(?:(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*)?(\d{4}))/i;
  const companyRegex = /(?:\s+(?:at|@|\||[-—])\s+)\s*([A-Z][A-Za-z0-9&.\s]{2,30})/;

  let totalYears = 0;
  const spans: { start: number; end: number }[] = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    for (const title of titlePatterns) {
      if (new RegExp(`\\b${title}\\b`, "i").test(line)) {
        let company: string | undefined = undefined;
        const compMatch = line.match(companyRegex);
        if (compMatch) {
          company = compMatch[1].replace(new RegExp(title, "i"), "").trim();
        } else if (i + 1 < lines.length && /^[A-Z][A-Za-z0-9\s,&]{2,30}$/.test(lines[i + 1]) && !dateRangeRegex.test(lines[i + 1])) {
          company = lines[i + 1].trim();
        }

        const context = lines.slice(i, Math.min(lines.length, i + 2)).join(" ");
        const dateMatch = context.match(dateRangeRegex);
        let duration: string | undefined = undefined;

        if (dateMatch) {
          duration = dateMatch[0].trim();
          const startYear = parseInt(dateMatch[2]);
          const endYear = /present|current|now/i.test(dateMatch[3]) ? 2026 : parseInt(dateMatch[dateMatch.length - 1]);
          if (!isNaN(startYear) && !isNaN(endYear) && endYear >= startYear) {
            spans.push({ start: startYear, end: endYear });
          }
        }

        let description: string | undefined = undefined;
        const nextLines = lines.slice(i + 1, Math.min(lines.length, i + 5));
        const bullets = nextLines.filter(l => l.trim().startsWith("-") || l.trim().startsWith("•") || l.trim().startsWith("*"));
        if (bullets.length > 0) {
          description = bullets.map(b => b.replace(/^[-•*]\s*/, "").trim()).join(". ");
        }

        roles.push({
          title,
          company: company || "Technology Corp",
          duration: duration || "Recent",
          description,
        });
        break;
      }
    }
  }

  if (spans.length > 0) {
    const minStart = Math.min(...spans.map(s => s.start));
    const maxEnd = Math.max(...spans.map(s => s.end));
    totalYears = Math.max(0.5, maxEnd - minStart);
  }

  const expMention = text.match(/(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)(?:\s+(?:of\s+)?experience)?/i);
  if (expMention) {
    const mentioned = parseFloat(expMention[1]);
    if (!isNaN(mentioned)) {
      totalYears = Math.max(totalYears, mentioned);
    }
  }

  if (totalYears === 0) {
    if (roles.length > 0) {
      totalYears = Math.max(1.0, roles.length * 1.5);
    } else {
      totalYears = 2.0;
    }
  }

  const rolesWithContext = roles.filter(r => r.duration !== "Recent" || (r.company && r.company !== "Technology Corp"));
  const candidatesToFilter = rolesWithContext.length > 0 ? rolesWithContext : roles;

  const uniqueRoles: ExtractedRole[] = [];
  for (const r of candidatesToFilter) {
    if (!uniqueRoles.some(u => u.title === r.title && (u.company === r.company || u.duration === r.duration))) {
      uniqueRoles.push(r);
    }
  }

  if (uniqueRoles.length === 0) {
    uniqueRoles.push({
      title: "Software & Technology Practitioner",
      company: "Industry Experience / Project Portfolio",
      duration: `${Math.round(totalYears * 10) / 10} yrs experience`,
      description: "Demonstrated project development and technical delivery.",
    });
  }

  return {
    roles: uniqueRoles,
    years_experience: Math.round(totalYears * 10) / 10,
  };
}

export function parseFullResume(text: string, filename?: string): ParsedResumeProfile {
  const name = extractNameFromText(text, filename);
  const contact = extractContactInfo(text);
  const skills = extractSkillsFromText(text);
  const { education, education_level } = extractEducation(text);
  const { roles, years_experience } = extractRolesAndExperience(text);

  return {
    id: "cand_" + Math.random().toString(36).substring(2, 9),
    filename,
    name,
    email: contact.email,
    phone: contact.phone,
    location: contact.location,
    linkedin: contact.linkedin,
    github: contact.github,
    skills,
    parsed_skills: skills,
    skills_extracted: skills,
    years_experience,
    education_level,
    education,
    roles,
    raw_text: text,
  };
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
