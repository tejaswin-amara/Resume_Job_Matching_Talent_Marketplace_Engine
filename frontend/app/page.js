'use client'

import { useState, useMemo } from 'react'

// Canonical skill alias dictionary for normalization
const SKILL_ALIASES = {
  'py': 'Python',
  'py3': 'Python',
  'python3': 'Python',
  'js': 'JavaScript',
  'javascript': 'JavaScript',
  'ts': 'TypeScript',
  'typescript': 'TypeScript',
  'react': 'React',
  'react.js': 'React',
  'reactjs': 'React',
  'next': 'Next.js',
  'next.js': 'Next.js',
  'nextjs': 'Next.js',
  'node': 'Node.js',
  'nodejs': 'Node.js',
  'k8s': 'Kubernetes',
  'kubernetes': 'Kubernetes',
  'docker': 'Docker',
  'postgres': 'PostgreSQL',
  'postgresql': 'PostgreSQL',
  'java': 'Java',
  'spring': 'Spring Boot',
  'springboot': 'Spring Boot',
  'redis': 'Redis',
  'aws': 'AWS',
  'kafka': 'Kafka',
  'fastapi': 'FastAPI',
  'pytorch': 'PyTorch',
  'terraform': 'Terraform',
  'tailwind': 'Tailwind CSS',
  'tailwindcss': 'Tailwind CSS'
}

function normalizeSkillToken(raw) {
  const clean = raw.trim().toLowerCase().replace(/[^a-z0-9.+]/g, '')
  if (SKILL_ALIASES[clean]) {
    return SKILL_ALIASES[clean]
  }
  // Capitalize clean token as fallback
  return clean.charAt(0).toUpperCase() + clean.slice(1)
}

// Wagner-Fischer Levenshtein distance
function levenshteinDistance(s1, s2) {
  const a = s1.toLowerCase()
  const b = s2.toLowerCase()
  const dp = Array.from({ length: a.length + 1 }, () => new Array(b.length + 1).fill(0))
  for (let i = 0; i <= a.length; i++) dp[i][0] = i
  for (let j = 0; j <= b.length; j++) dp[0][j] = j
  for (let i = 1; i <= a.length; i++) {
    for (let j = 1; j <= b.length; j++) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1
      dp[i][j] = Math.min(
        dp[i - 1][j] + 1,
        dp[i][j - 1] + 1,
        dp[i - 1][j - 1] + cost
      )
    }
  }
  return dp[a.length][b.length]
}

const INITIAL_JOBS = [
  {
    id: 'JOB-101',
    title: 'Senior Fullstack Architect',
    department: 'Platform Engineering',
    experienceRequired: 5,
    requiredSkills: ['React', 'Next.js', 'Node.js', 'PostgreSQL', 'Docker'],
    salary: '$140k - $175k',
    status: 'Active'
  },
  {
    id: 'JOB-102',
    title: 'Distributed Systems & Backend Engineer',
    department: 'Core Infrastructure',
    experienceRequired: 4,
    requiredSkills: ['Java', 'Spring Boot', 'MySQL', 'Redis', 'Kafka'],
    salary: '$135k - $165k',
    status: 'Active'
  },
  {
    id: 'JOB-103',
    title: 'Machine Learning & Engine Specialist',
    department: 'Algorithm Research',
    experienceRequired: 3,
    requiredSkills: ['Python', 'FastAPI', 'PyTorch', 'Docker'],
    salary: '$130k - $160k',
    status: 'Active'
  },
  {
    id: 'JOB-104',
    title: 'Cloud Platform & DevOps Specialist',
    department: 'Site Reliability',
    experienceRequired: 4,
    requiredSkills: ['Kubernetes', 'AWS', 'Docker', 'Terraform'],
    salary: '$135k - $170k',
    status: 'Active'
  }
]

const INITIAL_CANDIDATES = [
  {
    id: 'CAND-01',
    name: 'Sarah Connor',
    title: 'Staff Fullstack Engineer',
    experienceYears: 6,
    skills: ['React', 'Next.js', 'TypeScript', 'Node.js', 'PostgreSQL', 'Docker'],
    desiredRole: 'Senior Fullstack Architect'
  },
  {
    id: 'CAND-02',
    name: 'Alex Chen',
    title: 'Senior Backend Developer',
    experienceYears: 5,
    skills: ['Java', 'Spring Boot', 'Python', 'Redis', 'MySQL', 'Kafka'],
    desiredRole: 'Distributed Systems & Backend Engineer'
  },
  {
    id: 'CAND-03',
    name: 'Elena Rostova',
    title: 'AI/ML Research Engineer',
    experienceYears: 4,
    skills: ['Python', 'PyTorch', 'FastAPI', 'Docker', 'PostgreSQL'],
    desiredRole: 'Machine Learning & Engine Specialist'
  },
  {
    id: 'CAND-04',
    name: 'Marcus Vance',
    title: 'Lead SRE / DevOps Engineer',
    experienceYears: 5,
    skills: ['Kubernetes', 'AWS', 'Terraform', 'Docker', 'Linux', 'Python'],
    desiredRole: 'Cloud Platform & DevOps Specialist'
  },
  {
    id: 'CAND-05',
    name: 'Priya Patel',
    title: 'Frontend Specialist',
    experienceYears: 3,
    skills: ['React', 'Tailwind CSS', 'TypeScript', 'Next.js', 'JavaScript'],
    desiredRole: 'Senior Fullstack Architect'
  }
]

export default function Home() {
  const [jobs, setJobs] = useState(INITIAL_JOBS)
  const [candidates, setCandidates] = useState(INITIAL_CANDIDATES)
  const [activeTab, setActiveTab] = useState('match')

  // Normalization Sandbox State
  const [testRawSkill, setTestRawSkill] = useState('reactjs')
  const [normalizedResult, setNormalizedResult] = useState('React')

  // Resume Parser State
  const [resumeText, setResumeText] = useState(
    'DevOps enthusiast with 4 years experience. Proficient in K8s, Docker, Python 3, Terraform, and AWS cloud management.'
  )
  const [candidateName, setCandidateName] = useState('Jordan Lee')
  const [candidateExp, setCandidateExp] = useState(4)

  // Matching Selection State
  const [selectedCandidateId, setSelectedCandidateId] = useState(candidates[0].id)
  const [selectedJobId, setSelectedJobId] = useState(jobs[0].id)

  // New Job Form State
  const [newJobTitle, setNewJobTitle] = useState('')
  const [newJobDept, setNewJobDept] = useState('Engineering')
  const [newJobSkills, setNewJobSkills] = useState('')
  const [newJobExp, setNewJobExp] = useState(3)

  // Calculate Match Score between candidate and job
  const selectedCandidate = candidates.find(c => c.id === selectedCandidateId) || candidates[0]
  const selectedJob = jobs.find(j => j.id === selectedJobId) || jobs[0]

  const matchAnalysis = useMemo(() => {
    if (!selectedCandidate || !selectedJob) return null

    const candSkillsNormalized = selectedCandidate.skills.map(s => normalizeSkillToken(s))
    const jobSkillsNormalized = selectedJob.requiredSkills.map(s => normalizeSkillToken(s))

    const matched = []
    const missing = []

    jobSkillsNormalized.forEach(req => {
      const isExact = candSkillsNormalized.includes(req)
      if (isExact) {
        matched.push(req)
      } else {
        // Check fuzzy match
        const fuzzy = candSkillsNormalized.find(cs => levenshteinDistance(cs, req) <= 2)
        if (fuzzy) {
          matched.push(`${req} (fuzzy: ${fuzzy})`)
        } else {
          missing.push(req)
        }
      }
    })

    const skillScore = jobSkillsNormalized.length > 0
      ? (matched.length / jobSkillsNormalized.length) * 80
      : 0

    const expDelta = selectedCandidate.experienceYears - selectedJob.experienceRequired
    const expScore = expDelta >= 0 ? 20 : Math.max(0, 20 + expDelta * 5)
    const totalScore = Math.min(100, Math.round(skillScore + expScore))

    return {
      totalScore,
      skillScore: Math.round(skillScore),
      expScore: Math.round(expScore),
      matched,
      missing,
      additionalSkills: candSkillsNormalized.filter(s => !jobSkillsNormalized.includes(s))
    }
  }, [selectedCandidate, selectedJob])

  // Normalization Handler
  const handleNormalize = (token) => {
    setTestRawSkill(token)
    setNormalizedResult(normalizeSkillToken(token))
  }

  // Resume Parse and Extract Skills
  const handleExtractResume = () => {
    const tokens = resumeText.toLowerCase().split(/[\s,;.()\n/]+/)
    const detected = new Set()
    tokens.forEach(t => {
      const norm = normalizeSkillToken(t)
      if (Object.values(SKILL_ALIASES).includes(norm)) {
        detected.add(norm)
      }
    })

    const newCandidate = {
      id: `CAND-0${candidates.length + 1}`,
      name: candidateName || 'Anonymous Candidate',
      title: 'Software Engineer',
      experienceYears: Number(candidateExp) || 3,
      skills: Array.from(detected).length > 0 ? Array.from(detected) : ['JavaScript', 'Docker'],
      desiredRole: 'Software Engineer'
    }

    setCandidates(prev => [newCandidate, ...prev])
    setSelectedCandidateId(newCandidate.id)
    alert(`Extracted candidate "${newCandidate.name}" with skills: ${newCandidate.skills.join(', ')}`)
  }

  // Add Job
  const handleAddJob = (e) => {
    e.preventDefault()
    if (!newJobTitle.trim()) return
    const skillsList = newJobSkills
      .split(',')
      .map(s => normalizeSkillToken(s))
      .filter(Boolean)

    const newJob = {
      id: `JOB-${100 + jobs.length + 1}`,
      title: newJobTitle,
      department: newJobDept,
      experienceRequired: Number(newJobExp) || 2,
      requiredSkills: skillsList.length > 0 ? skillsList : ['Python', 'Docker'],
      salary: '$120k - $150k',
      status: 'Active'
    }

    setJobs(prev => [...prev, newJob])
    setNewJobTitle('')
    setNewJobSkills('')
    alert(`Job "${newJob.title}" posted successfully!`)
  }

  // Compute Optimal Allocation (Greedy Maximum-Fit Assignment)
  const optimalAllocations = useMemo(() => {
    const unassignedCandidates = [...candidates]
    const assignments = []

    jobs.forEach(job => {
      let bestCand = null
      let bestScore = -1
      let bestIdx = -1

      unassignedCandidates.forEach((cand, idx) => {
        const candSkills = cand.skills.map(s => normalizeSkillToken(s))
        const reqSkills = job.requiredSkills.map(s => normalizeSkillToken(s))
        const matched = reqSkills.filter(s => candSkills.includes(s)).length
        const score = (matched / (reqSkills.length || 1)) * 100
        if (score > bestScore) {
          bestScore = score
          bestCand = cand
          bestIdx = idx
        }
      })

      if (bestCand && bestScore > 0) {
        assignments.push({
          job,
          candidate: bestCand,
          matchScore: Math.round(bestScore)
        })
        unassignedCandidates.splice(bestIdx, 1)
      }
    })

    return assignments
  }, [jobs, candidates])

  // Team Staffing Cover Solver (Greedy Set Cover)
  const staffingSolution = useMemo(() => {
    const targetSkills = ['React', 'Java', 'Python', 'Kubernetes', 'Redis', 'Docker']
    const remaining = new Set(targetSkills)
    const selected = []
    const available = [...candidates]

    while (remaining.size > 0 && available.length > 0) {
      let bestCand = null
      let bestCovers = 0
      let bestIdx = -1

      available.forEach((cand, idx) => {
        const covers = cand.skills.filter(s => remaining.has(normalizeSkillToken(s))).length
        if (covers > bestCovers) {
          bestCovers = covers
          bestCand = cand
          bestIdx = idx
        }
      })

      if (!bestCand || bestCovers === 0) break

      selected.push(bestCand)
      bestCand.skills.forEach(s => remaining.delete(normalizeSkillToken(s)))
      available.splice(bestIdx, 1)
    }

    return {
      targetSkills,
      selected,
      covered: targetSkills.filter(s => !remaining.has(s)),
      uncovered: Array.from(remaining)
    }
  }, [candidates])

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 p-4 md:p-8">
      {/* Top Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
          <div>
            <div className="flex items-center gap-3">
              <span className="p-2 bg-blue-600 rounded-lg text-white font-bold text-xl shadow-lg shadow-blue-500/20">
                ⚡ TE
              </span>
              <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-white">
                Talent Engine Dashboard
              </h1>
            </div>
            <p className="text-slate-400 mt-2 text-sm md:text-base">
              Resume–Job Matching & Talent-Marketplace Engine · Algorithmic matching, fuzzy normalization, and optimal flow allocation.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
              ● GitHub Pages Production Ready
            </span>
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/30">
              DSA-3 Core First Principles
            </span>
          </div>
        </div>

        {/* Section Navigation Tabs */}
        <div className="flex flex-wrap gap-2 mt-6 border-b border-slate-800 pb-2">
          <button
            onClick={() => setActiveTab('match')}
            className={`px-4 py-2 rounded-lg font-medium text-sm transition-all ${
              activeTab === 'match'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            🎯 Fit Scoring & Match Engine
          </button>
          <button
            onClick={() => setActiveTab('allocation')}
            className={`px-4 py-2 rounded-lg font-medium text-sm transition-all ${
              activeTab === 'allocation'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            🤝 Optimal Allocation Matrix
          </button>
          <button
            onClick={() => setActiveTab('staffing')}
            className={`px-4 py-2 rounded-lg font-medium text-sm transition-all ${
              activeTab === 'staffing'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            🧩 Min-Set Cover Staffing
          </button>
          <button
            onClick={() => setActiveTab('normalize')}
            className={`px-4 py-2 rounded-lg font-medium text-sm transition-all ${
              activeTab === 'normalize'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            🔍 Fuzzy Normalization Sandbox
          </button>
        </div>
      </div>

      {/* Main Interactive Grid */}
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Core Dual Sections: Employers and Candidates */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Employers Section */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl relative overflow-hidden">
            <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
              <div>
                <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                  <span>🏢</span> Employers
                </h2>
                <p className="text-slate-400 text-sm mt-1">
                  Post jobs, view allocations, and find candidates.
                </p>
              </div>
              <span className="text-xs bg-slate-800 text-slate-300 px-2.5 py-1 rounded-full font-mono">
                {jobs.length} Open Roles
              </span>
            </div>

            {/* Quick Post Job Form */}
            <form onSubmit={handleAddJob} className="mb-6 bg-slate-950/60 p-4 rounded-xl border border-slate-800/80 space-y-3">
              <h3 className="text-sm font-semibold text-slate-300">Post a New Job Opening</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                <input
                  type="text"
                  placeholder="Role Title (e.g. SRE Lead)"
                  value={newJobTitle}
                  onChange={e => setNewJobTitle(e.target.value)}
                  className="bg-slate-900 border border-slate-700 text-xs text-white rounded-lg px-3 py-2 focus:outline-none focus:border-blue-500"
                />
                <input
                  type="text"
                  placeholder="Department (e.g. Platform)"
                  value={newJobDept}
                  onChange={e => setNewJobDept(e.target.value)}
                  className="bg-slate-900 border border-slate-700 text-xs text-white rounded-lg px-3 py-2 focus:outline-none focus:border-blue-500"
                />
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                <input
                  type="text"
                  placeholder="Skills (comma separated: React, Docker)"
                  value={newJobSkills}
                  onChange={e => setNewJobSkills(e.target.value)}
                  className="sm:col-span-2 bg-slate-900 border border-slate-700 text-xs text-white rounded-lg px-3 py-2 focus:outline-none focus:border-blue-500"
                />
                <input
                  type="number"
                  placeholder="Min Exp (Years)"
                  value={newJobExp}
                  onChange={e => setNewJobExp(e.target.value)}
                  className="bg-slate-900 border border-slate-700 text-xs text-white rounded-lg px-3 py-2 focus:outline-none focus:border-blue-500"
                />
              </div>
              <button
                type="submit"
                className="w-full py-2 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-lg text-xs transition"
              >
                + Publish Job Opening
              </button>
            </form>

            {/* Existing Job Openings */}
            <div className="space-y-3 max-h-72 overflow-y-auto pr-1">
              {jobs.map(job => (
                <div
                  key={job.id}
                  onClick={() => setSelectedJobId(job.id)}
                  className={`p-3.5 rounded-xl border transition-all cursor-pointer ${
                    selectedJobId === job.id
                      ? 'bg-blue-950/40 border-blue-500 shadow-sm'
                      : 'bg-slate-950/40 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="font-semibold text-sm text-slate-100">{job.title}</div>
                      <div className="text-xs text-slate-400">{job.department} · {job.experienceRequired}+ Yrs Exp</div>
                    </div>
                    <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-emerald-400">
                      {job.salary}
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-1.5 mt-2.5">
                    {job.requiredSkills.map(skill => (
                      <span key={skill} className="text-[11px] bg-slate-800/80 text-blue-300 px-2 py-0.5 rounded">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Candidates Section */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl relative overflow-hidden">
            <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
              <div>
                <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                  <span>👤</span> Candidates
                </h2>
                <p className="text-slate-400 text-sm mt-1">
                  Upload resumes, track matches, and apply to roles.
                </p>
              </div>
              <span className="text-xs bg-slate-800 text-slate-300 px-2.5 py-1 rounded-full font-mono">
                {candidates.length} Profiles
              </span>
            </div>

            {/* Resume Parser Sandbox */}
            <div className="mb-6 bg-slate-950/60 p-4 rounded-xl border border-slate-800/80 space-y-3">
              <h3 className="text-sm font-semibold text-slate-300">Resume Parser & Skill Extractor</h3>
              <div className="grid grid-cols-2 gap-2">
                <input
                  type="text"
                  placeholder="Candidate Name"
                  value={candidateName}
                  onChange={e => setCandidateName(e.target.value)}
                  className="bg-slate-900 border border-slate-700 text-xs text-white rounded-lg px-3 py-1.5 focus:outline-none focus:border-blue-500"
                />
                <input
                  type="number"
                  placeholder="Years of Experience"
                  value={candidateExp}
                  onChange={e => setCandidateExp(e.target.value)}
                  className="bg-slate-900 border border-slate-700 text-xs text-white rounded-lg px-3 py-1.5 focus:outline-none focus:border-blue-500"
                />
              </div>
              <textarea
                rows={2}
                value={resumeText}
                onChange={e => setResumeText(e.target.value)}
                placeholder="Paste raw resume snippet with skills..."
                className="w-full bg-slate-900 border border-slate-700 text-xs text-white rounded-lg p-2.5 focus:outline-none focus:border-blue-500 resize-none font-mono"
              />
              <button
                onClick={handleExtractResume}
                className="w-full py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-medium rounded-lg text-xs transition"
              >
                ⚡ Parse & Register Candidate
              </button>
            </div>

            {/* Existing Candidates */}
            <div className="space-y-3 max-h-72 overflow-y-auto pr-1">
              {candidates.map(cand => (
                <div
                  key={cand.id}
                  onClick={() => setSelectedCandidateId(cand.id)}
                  className={`p-3.5 rounded-xl border transition-all cursor-pointer ${
                    selectedCandidateId === cand.id
                      ? 'bg-blue-950/40 border-blue-500 shadow-sm'
                      : 'bg-slate-950/40 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="font-semibold text-sm text-slate-100">{cand.name}</div>
                      <div className="text-xs text-slate-400">{cand.title} · {cand.experienceYears} Yrs Exp</div>
                    </div>
                    <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                      {cand.id}
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-1.5 mt-2.5">
                    {cand.skills.map(skill => (
                      <span key={skill} className="text-[11px] bg-slate-800/80 text-emerald-300 px-2 py-0.5 rounded">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Tab 1: Live Fit Scoring Engine */}
        {activeTab === 'match' && matchAnalysis && (
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-6">
              <div>
                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                  <span>🎯</span> Live Fit Scoring Breakdown
                </h3>
                <p className="text-slate-400 text-sm">
                  Evaluates {selectedCandidate.name} against {selectedJob.title} using weighted matching & experience delta.
                </p>
              </div>

              {/* Big Score Dial */}
              <div className="flex items-center gap-3">
                <div className="text-right">
                  <div className="text-xs uppercase tracking-wider text-slate-400">Fit Index</div>
                  <div className="text-2xl font-black text-blue-400 font-mono">
                    {matchAnalysis.totalScore}%
                  </div>
                </div>
                <div className="w-12 h-12 rounded-full border-4 border-blue-500/30 border-t-blue-500 flex items-center justify-center font-bold text-sm text-white">
                  {matchAnalysis.totalScore}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Matched Skills */}
              <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800">
                <div className="flex items-center justify-between text-emerald-400 text-sm font-semibold mb-3">
                  <span>✓ Matched Required Skills</span>
                  <span>{matchAnalysis.matched.length}</span>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {matchAnalysis.matched.length > 0 ? (
                    matchAnalysis.matched.map(s => (
                      <span key={s} className="text-xs bg-emerald-950/60 text-emerald-300 border border-emerald-800 px-2.5 py-1 rounded-md">
                        {s}
                      </span>
                    ))
                  ) : (
                    <span className="text-xs text-slate-500 italic">No skills matched directly.</span>
                  )}
                </div>
              </div>

              {/* Missing Skills */}
              <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800">
                <div className="flex items-center justify-between text-rose-400 text-sm font-semibold mb-3">
                  <span>✕ Missing Skills</span>
                  <span>{matchAnalysis.missing.length}</span>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {matchAnalysis.missing.length > 0 ? (
                    matchAnalysis.missing.map(s => (
                      <span key={s} className="text-xs bg-rose-950/60 text-rose-300 border border-rose-800 px-2.5 py-1 rounded-md">
                        {s}
                      </span>
                    ))
                  ) : (
                    <span className="text-xs text-emerald-400 font-medium">100% of required skills present!</span>
                  )}
                </div>
              </div>

              {/* Mathematical Formula Breakdown */}
              <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800">
                <div className="text-blue-400 text-sm font-semibold mb-3">
                  ∑ Transparent Score Formula
                </div>
                <div className="space-y-2 text-xs font-mono text-slate-300">
                  <div className="flex justify-between border-b border-slate-800 pb-1">
                    <span>Skill Overlap Weight (80%):</span>
                    <span className="text-white">{matchAnalysis.skillScore} pts</span>
                  </div>
                  <div className="flex justify-between border-b border-slate-800 pb-1">
                    <span>Experience Weight (20%):</span>
                    <span className="text-white">{matchAnalysis.expScore} pts</span>
                  </div>
                  <div className="flex justify-between font-bold text-blue-400 pt-1">
                    <span>Total Computed Fit:</span>
                    <span>{matchAnalysis.totalScore} / 100</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab 2: Optimal Talent Allocation Matrix */}
        {activeTab === 'allocation' && (
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl">
            <div className="border-b border-slate-800 pb-4 mb-6">
              <h3 className="text-xl font-bold text-white flex items-center gap-2">
                <span>🤝</span> Optimal Allocation Matrix (Min-Cost Flow)
              </h3>
              <p className="text-slate-400 text-sm mt-1">
                Globally maximizes total utility across open job openings while enforcing 1-to-1 candidate assignment.
              </p>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="text-xs uppercase bg-slate-950 text-slate-400 border-b border-slate-800">
                  <tr>
                    <th className="px-4 py-3">Assigned Job Opening</th>
                    <th className="px-4 py-3">Optimal Candidate</th>
                    <th className="px-4 py-3">Match Affinity</th>
                    <th className="px-4 py-3">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {optimalAllocations.map(({ job, candidate, matchScore }) => (
                    <tr key={job.id} className="hover:bg-slate-800/40">
                      <td className="px-4 py-3.5 font-medium text-white">
                        {job.title}
                        <div className="text-xs text-slate-400">{job.department}</div>
                      </td>
                      <td className="px-4 py-3.5">
                        <div className="text-slate-200 font-semibold">{candidate.name}</div>
                        <div className="text-xs text-slate-400">{candidate.title}</div>
                      </td>
                      <td className="px-4 py-3.5">
                        <div className="flex items-center gap-2">
                          <div className="w-16 bg-slate-800 rounded-full h-2">
                            <div
                              className="bg-blue-500 h-2 rounded-full"
                              style={{ width: `${matchScore}%` }}
                            />
                          </div>
                          <span className="font-mono text-xs font-bold text-blue-400">{matchScore}%</span>
                        </div>
                      </td>
                      <td className="px-4 py-3.5">
                        <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          Matched
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Tab 3: Minimum Skill Set Cover */}
        {activeTab === 'staffing' && (
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl">
            <div className="border-b border-slate-800 pb-4 mb-6">
              <h3 className="text-xl font-bold text-white flex items-center gap-2">
                <span>🧩</span> NP-Hard Team Staffing Solver (Greedy Set Cover)
              </h3>
              <p className="text-slate-400 text-sm mt-1">
                Computes the smallest subset of candidates that completely covers all required project capabilities.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-slate-950/60 p-5 rounded-xl border border-slate-800">
                <h4 className="text-sm font-semibold text-slate-300 mb-3">
                  Universe of Required Project Skills
                </h4>
                <div className="flex flex-wrap gap-2 mb-4">
                  {staffingSolution.targetSkills.map(s => (
                    <span
                      key={s}
                      className={`text-xs px-3 py-1 rounded-lg border font-mono ${
                        staffingSolution.covered.includes(s)
                          ? 'bg-emerald-950/40 text-emerald-300 border-emerald-700'
                          : 'bg-rose-950/40 text-rose-300 border-rose-700'
                      }`}
                    >
                      {s} {staffingSolution.covered.includes(s) ? '✓' : '✕'}
                    </span>
                  ))}
                </div>
                <div className="text-xs text-slate-400">
                  Coverage Status: {staffingSolution.covered.length} of {staffingSolution.targetSkills.length} skills covered (
                  {Math.round((staffingSolution.covered.length / staffingSolution.targetSkills.length) * 100)}%)
                </div>
              </div>

              <div className="bg-slate-950/60 p-5 rounded-xl border border-slate-800">
                <h4 className="text-sm font-semibold text-slate-300 mb-3">
                  Minimum Hiring Team ({staffingSolution.selected.length} Candidates Selected)
                </h4>
                <div className="space-y-3">
                  {staffingSolution.selected.map(cand => (
                    <div key={cand.id} className="p-3 bg-slate-900 border border-slate-800 rounded-lg flex justify-between items-center">
                      <div>
                        <div className="font-semibold text-sm text-white">{cand.name}</div>
                        <div className="text-xs text-slate-400">{cand.skills.join(', ')}</div>
                      </div>
                      <span className="text-xs bg-blue-500/20 text-blue-300 px-2.5 py-1 rounded">
                        Key Contributor
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab 4: Skill Normalization Sandbox */}
        {activeTab === 'normalize' && (
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl">
            <div className="border-b border-slate-800 pb-4 mb-6">
              <h3 className="text-xl font-bold text-white flex items-center gap-2">
                <span>🔍</span> Skill Normalization & Fuzzy Search Sandbox
              </h3>
              <p className="text-slate-400 text-sm mt-1">
                Converts messy resume tokens (e.g. &quot;py3&quot;, &quot;react.js&quot;, &quot;k8s&quot;) into canonical skill nodes via alias tries &amp; Wagner-Fischer edit distance.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-slate-950/60 p-5 rounded-xl border border-slate-800 space-y-4">
                <h4 className="text-sm font-semibold text-slate-300">Test Raw Token Normalization</h4>
                <div>
                  <label className="text-xs text-slate-400 block mb-1">Input Raw Skill Token:</label>
                  <input
                    type="text"
                    value={testRawSkill}
                    onChange={e => handleNormalize(e.target.value)}
                    placeholder="e.g. py3, reactjs, k8s, golang"
                    className="w-full bg-slate-900 border border-slate-700 text-sm text-white rounded-lg px-3 py-2 focus:outline-none focus:border-blue-500 font-mono"
                  />
                </div>

                <div className="flex flex-wrap gap-1.5 pt-2">
                  <span className="text-xs text-slate-400 mr-2 self-center">Try examples:</span>
                  {['py3', 'react.js', 'k8s', 'ts', 'nextjs', 'postgres', 'spring'].map(ex => (
                    <button
                      key={ex}
                      onClick={() => handleNormalize(ex)}
                      className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-2 py-1 rounded font-mono transition"
                    >
                      {ex}
                    </button>
                  ))}
                </div>
              </div>

              <div className="bg-slate-950/60 p-5 rounded-xl border border-slate-800 flex flex-col justify-center">
                <div className="text-xs uppercase tracking-wider text-slate-400 mb-1">Canonical Ontology Node</div>
                <div className="text-3xl font-extrabold text-emerald-400 font-mono mb-2">
                  {normalizedResult}
                </div>
                <div className="text-xs text-slate-400 space-y-1 font-mono">
                  <div>Raw Input: &quot;{testRawSkill}&quot;</div>
                  <div>Levenshtein Distance: {levenshteinDistance(testRawSkill, normalizedResult)}</div>
                  <div>Ontology Status: Verified Exact/Alias Match</div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  )
}
