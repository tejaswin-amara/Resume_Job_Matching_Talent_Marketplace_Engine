import asyncio

from core.engine.string.aho_corasick import AhoCorasickAutomaton
from db.models import Candidate, CandidateSkill, JobPosting, JobSkillRequirement, Skill
from db.models.base import Base
from db.session import async_session_maker, engine

SKILLS = [
    "python",
    "java",
    "c++",
    "go",
    "rust",
    "javascript",
    "typescript",
    "react",
    "angular",
    "vue",
    "node.js",
    "django",
    "flask",
    "fastapi",
    "spring boot",
    "aws",
    "gcp",
    "azure",
    "docker",
    "kubernetes",
    "sql",
    "postgresql",
    "mysql",
    "mongodb",
    "redis",
    "elasticsearch",
    "kafka",
    "rabbitmq",
]

JOBS = [
    {
        "title": "Senior Python Backend Engineer",
        "desc": "Looking for 5+ years exp in Python, FastAPI, PostgreSQL, Docker.",
        "min_exp": 5.0,
        "skills": ["python", "fastapi", "postgresql", "docker", "sql"],
    },
    {
        "title": "Frontend React Developer",
        "desc": "Need a React specialist with 3+ years experience. TypeScript is a must.",
        "min_exp": 3.0,
        "skills": ["javascript", "typescript", "react"],
    },
    {
        "title": "DevOps Engineer",
        "desc": "Kubernetes, AWS, and Docker expert needed.",
        "min_exp": 4.0,
        "skills": ["aws", "docker", "kubernetes"],
    },
]

CANDIDATES = [
    {
        "name": "Alice Smith",
        "email": "alice@example.com",
        "text": "I am a Senior Backend Engineer with 6 years of experience in Python, FastAPI, and PostgreSQL. I also use Docker and Kubernetes.",
        "exp": 6.0,
    },
    {
        "name": "Bob Jones",
        "email": "bob@example.com",
        "text": "Frontend developer. 4 years working with React, JavaScript, and TypeScript.",
        "exp": 4.0,
    },
    {
        "name": "Charlie Brown",
        "email": "charlie@example.com",
        "text": "DevOps guy. 5 years of AWS, Docker, Kubernetes, and some Python.",
        "exp": 5.0,
    },
]


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        # Create skills
        skill_objs = {}
        for s in SKILLS:
            skill = Skill(name=s, category="Tech")
            session.add(skill)
            skill_objs[s] = skill
        await session.commit()

        # Extractor
        automaton = AhoCorasickAutomaton()
        for s in SKILLS:
            automaton.add_word(s)
        automaton.build()

        # Create jobs
        for j in JOBS:
            job = JobPosting(
                title=j["title"],
                description=j["desc"],
                requirements=j["desc"],
                min_experience=j["min_exp"],
                embedding=[0.0] * 384,
            )
            session.add(job)
            await session.flush()

            for s in j["skills"]:
                if s in skill_objs:
                    session.add(JobSkillRequirement(job_id=job.id, skill_id=skill_objs[s].id))

        # Create candidates
        for c in CANDIDATES:
            cand = Candidate(
                name=c["name"],
                email=c["email"],
                raw_text=c["text"],
                total_experience_years=c["exp"],
                embedding=[0.0] * 384,
            )
            session.add(cand)
            await session.flush()

            matches = automaton.search(c["text"].lower())
            found_skills = {match[1] for match in matches}
            for s in found_skills:
                if s in skill_objs:
                    session.add(CandidateSkill(candidate_id=cand.id, skill_id=skill_objs[s].id))

        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed())
