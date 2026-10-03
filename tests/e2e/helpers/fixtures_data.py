"""Golden fixture datasets for E2E opaque-box testing.

Contains realistic candidate resumes, job requisitions, skill taxonomies,
raw byte streams (PDF/DOCX/TXT), and adversarial boundary inputs.
"""

from __future__ import annotations

from typing import Any

# Standard magic bytes for document testing
PDF_MAGIC_BYTES = (
    b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
    + b"Realistic candidate resume text stream in PDF format. Skills: Python, FastAPI, Docker. Experience: 5 years."
)
DOCX_MAGIC_BYTES = (
    b"PK\x03\x04\x14\x00\x06\x00"
    + b"Realistic candidate resume text in DOCX zip stream. Skills: React, TypeScript, Next.js. Experience: 3 years."
)
TXT_SAMPLE_BYTES = b"Jane Doe\nEmail: jane.doe@example.com\nSkills: Python, SQL, AWS, Kubernetes\nExperience: 7 years\nEducation: Master of Science in Computer Science"

SAMPLE_SKILLS_TAXONOMY: list[str] = [
    "Python",
    "FastAPI",
    "PostgreSQL",
    "Docker",
    "Kubernetes",
    "AWS",
    "GCP",
    "React",
    "TypeScript",
    "JavaScript",
    "Next.js",
    "Tailwind CSS",
    "HTML",
    "CSS",
    "PyTorch",
    "TensorFlow",
    "NLP",
    "SentenceTransformers",
    "pgvector",
    "Machine Learning",
    "Go",
    "Rust",
    "Java",
    "C++",
    "SQL",
    "Redis",
    "Kafka",
    "GraphQL",
    "CI/CD",
    "Git",
    "Linux",
    "Microservices",
    "REST API",
    "Algorithms",
    "Data Structures",
]

CANDIDATES_FIXTURES: list[dict[str, Any]] = [
    {
        "id": 1,
        "name": "Alex Mercer",
        "email": "alex.mercer@example.com",
        "phone": "+1-555-0101",
        "title": "Senior Full-Stack Engineer",
        "skills": [
            "Python",
            "FastAPI",
            "PostgreSQL",
            "Docker",
            "React",
            "TypeScript",
            "Tailwind CSS",
        ],
        "years_experience": 6.5,
        "education": "Master of Science in Computer Science",
        "education_level": 4,  # e.g., 1: High School, 2: Associate, 3: Bachelor, 4: Master, 5: PhD
        "raw_text": (
            "Alex Mercer\nSenior Full-Stack Engineer\n"
            "Email: alex.mercer@example.com | Phone: +1-555-0101\n"
            "Professional Summary:\n"
            "6+ years designing scalable cloud backends and responsive web applications.\n"
            "Core Competencies: Python, FastAPI, PostgreSQL, Docker, React, TypeScript, Tailwind CSS.\n"
            "Experience:\n"
            "Senior Backend Engineer at TechCorp (2020 - Present): Designed REST APIs using FastAPI and PostgreSQL with pgvector.\n"
            "Full Stack Developer at WebSolutions (2018 - 2020): Built frontends with React and TypeScript.\n"
            "Education:\n"
            "Master of Science in Computer Science, State University, 2018."
        ),
    },
    {
        "id": 2,
        "name": "Elena Rostova",
        "email": "elena.rostova@example.com",
        "phone": "+1-555-0102",
        "title": "AI/ML Research Engineer",
        "skills": [
            "Python",
            "PyTorch",
            "NLP",
            "SentenceTransformers",
            "pgvector",
            "Machine Learning",
            "Docker",
        ],
        "years_experience": 4.0,
        "education": "Doctor of Philosophy in Artificial Intelligence",
        "education_level": 5,
        "raw_text": (
            "Elena Rostova, Ph.D.\n"
            "AI/ML Research Engineer | elena.rostova@example.com\n"
            "Specialist in natural language processing, vector similarity search, and deep learning architectures.\n"
            "Skills: Python, PyTorch, NLP, SentenceTransformers, pgvector, Machine Learning, Docker, SQL.\n"
            "Experience:\n"
            "Machine Learning Scientist at DeepMind AI (2022 - Present): Implemented embedding retrieval pipelines with pgvector.\n"
            "AI Researcher at AI Labs (2020 - 2022): Fine-tuned Transformer models for semantic text ranking.\n"
            "Education: Ph.D. in Computer Science (Artificial Intelligence), Stanford University, 2020."
        ),
    },
    {
        "id": 3,
        "name": "Jordan Smith",
        "email": "jordan.smith@example.com",
        "phone": "+1-555-0103",
        "title": "Junior Frontend Developer",
        "skills": ["JavaScript", "React", "HTML", "CSS", "Git"],
        "years_experience": 1.2,
        "education": "Bachelor of Science in Information Systems",
        "education_level": 3,
        "raw_text": (
            "Jordan Smith\nJunior Web Developer\n"
            "Email: jordan.smith@example.com\n"
            "Recent graduate with 1 year professional experience in building web interfaces.\n"
            "Technical Skills: JavaScript, React, HTML, CSS, Git, Tailwind CSS basics.\n"
            "Experience:\n"
            "Junior Frontend Developer at StartupX (2025 - Present): Built UI components in React.\n"
            "Education:\n"
            "B.S. in Information Systems, 2025."
        ),
    },
    {
        "id": 4,
        "name": "Marcus Vance",
        "email": "marcus.vance@example.com",
        "phone": "+1-555-0104",
        "title": "Principal Systems & Cloud Architect",
        "skills": [
            "Kubernetes",
            "Docker",
            "AWS",
            "Go",
            "Python",
            "Kafka",
            "Microservices",
            "Linux",
        ],
        "years_experience": 12.0,
        "education": "Bachelor of Science in Computer Engineering",
        "education_level": 3,
        "raw_text": (
            "Marcus Vance | Principal Cloud Architect\n"
            "marcus.vance@example.com | 12+ years experience in distributed cloud infrastructure.\n"
            "Skills: Kubernetes, Docker, AWS, Go, Python, Kafka, Microservices, Linux, CI/CD, Redis.\n"
            "Experience:\n"
            "Principal Architect at EnterpriseCloud (2018 - Present): Orchestrated multi-region Kubernetes clusters on AWS.\n"
            "Education: B.S. Computer Engineering, 2014."
        ),
    },
    {
        "id": 5,
        "name": "Sofia Gomez",
        "email": "sofia.gomez@example.com",
        "phone": "+1-555-0105",
        "title": "Data Engineer",
        "skills": ["Python", "SQL", "PostgreSQL", "Kafka", "Docker", "AWS"],
        "years_experience": 5.0,
        "education": "Master of Science in Data Analytics",
        "education_level": 4,
        "raw_text": (
            "Sofia Gomez\nData Engineer\n"
            "Email: sofia.gomez@example.com\n"
            "5 years building high-throughput ETL and streaming pipelines.\n"
            "Skills: Python, SQL, PostgreSQL, Kafka, Docker, AWS.\n"
            "Education: M.S. Data Analytics, 2021."
        ),
    },
]

JOB_REQUISITIONS_FIXTURES: list[dict[str, Any]] = [
    {
        "id": 101,
        "title": "Senior Full-Stack Engineer",
        "description": "We are seeking a Senior Full-Stack Engineer proficient in Python, FastAPI, and TypeScript with React.",
        "required_skills": ["Python", "FastAPI", "TypeScript"],
        "preferred_skills": ["PostgreSQL", "Docker", "Tailwind CSS"],
        "min_experience_years": 5.0,
        "required_education_level": 3,  # Bachelor
        "capacity": 2,
    },
    {
        "id": 102,
        "title": "Lead Machine Learning Engineer",
        "description": "Looking for an NLP / ML Engineer to lead vector search matching engine development with PyTorch and pgvector.",
        "required_skills": ["Python", "PyTorch", "NLP", "Machine Learning"],
        "preferred_skills": ["SentenceTransformers", "pgvector", "Docker"],
        "min_experience_years": 4.0,
        "required_education_level": 4,  # Master
        "capacity": 1,
    },
    {
        "id": 103,
        "title": "Entry-Level Frontend Developer",
        "description": "Great opportunity for junior talent to work on modern React interfaces.",
        "required_skills": ["JavaScript", "HTML", "CSS"],
        "preferred_skills": ["React", "Git"],
        "min_experience_years": 0.0,
        "required_education_level": 2,  # Associate or self-taught
        "capacity": 2,
    },
    {
        "id": 104,
        "title": "Cloud Infrastructure Lead",
        "description": "Lead DevOps and Cloud infrastructure migration on AWS with Kubernetes and Go microservices.",
        "required_skills": ["Kubernetes", "AWS", "Docker"],
        "preferred_skills": ["Go", "Kafka", "Linux"],
        "min_experience_years": 8.0,
        "required_education_level": 3,
        "capacity": 1,
    },
]

# Adversarial & Boundary Test Inputs
ADVERSARIAL_INPUTS: dict[str, Any] = {
    "empty_resume": {
        "text": "",
        "skills": [],
        "years_experience": 0.0,
        "education_level": 0,
    },
    "whitespace_only": {
        "text": "   \n\t   \r\n   ",
        "skills": [],
        "years_experience": 0.0,
        "education_level": 0,
    },
    "zero_requirement_job": {
        "title": "General Associate",
        "description": "No prior experience or specific skills strictly required.",
        "required_skills": [],
        "preferred_skills": [],
        "min_experience_years": 0.0,
        "required_education_level": 0,
        "capacity": 1,
    },
    "extreme_skills_job": {
        "title": "Unicorn Architect",
        "description": "Requires all technologies in existence.",
        "required_skills": SAMPLE_SKILLS_TAXONOMY,
        "preferred_skills": [],
        "min_experience_years": 25.0,
        "required_education_level": 5,
        "capacity": 1,
    },
    "unicode_and_emojis": {
        "text": "🚀 Senior Developer 💻 🐍 Python & ⚛️ React enthusiast! 🌟 Experience: 10 années. Éducation: Diplôme d'Ingénieur.",
        "skills": ["Python", "React"],
        "years_experience": 10.0,
        "education_level": 4,
    },
    "profane_text": {
        "text": "Senior Developer with strong damn Python skills and kickass badass Docker experience.",
        "skills": ["Python", "Docker"],
        "years_experience": 3.0,
    },
    "massive_text": {
        "text": (
            "Senior Software Engineer. Skills: Python, Docker, Kubernetes. " * 5000
        ),  # ~300KB text
        "skills": ["Python", "Docker", "Kubernetes"],
        "years_experience": 8.0,
        "education_level": 3,
    },
}
