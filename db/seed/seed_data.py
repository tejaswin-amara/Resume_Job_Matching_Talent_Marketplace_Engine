import asyncio

from core.engine.string.aho_corasick import AhoCorasickAutomaton
from db.models import Candidate, CandidateSkill, JobPosting, JobSkillRequirement, Skill
from db.session import get_sessionmaker

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
    {
        "title": "Data Engineer",
        "desc": "Experience in Python, SQL, PostgreSQL and building data pipelines.",
        "min_exp": 3.0,
        "skills": ["python", "sql", "postgresql"],
    },
    {
        "title": "Full Stack Engineer",
        "desc": "React, Node.js, TypeScript, PostgreSQL",
        "min_exp": 4.0,
        "skills": ["react", "node.js", "typescript", "postgresql"],
    },
    {
        "title": "Machine Learning Engineer",
        "desc": "Python, AWS, PyTorch (using python proxy).",
        "min_exp": 3.0,
        "skills": ["python", "aws"],
    },
    {
        "title": "Cloud Architect",
        "desc": "AWS, GCP, Kubernetes, Docker",
        "min_exp": 8.0,
        "skills": ["aws", "gcp", "kubernetes", "docker"],
    },
    {
        "title": "Backend Go Developer",
        "desc": "Go, PostgreSQL, Docker, Kubernetes.",
        "min_exp": 4.0,
        "skills": ["go", "postgresql", "docker", "kubernetes"],
    },
    {
        "title": "Frontend Vue Developer",
        "desc": "Vue, JavaScript, HTML, CSS",
        "min_exp": 2.0,
        "skills": ["vue", "javascript"],
    },
    {
        "title": "Security Engineer",
        "desc": "Python, AWS, Linux, Security.",
        "min_exp": 5.0,
        "skills": ["python", "aws"],
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
    {
        "name": "David Clark",
        "email": "david@example.com",
        "text": "Data Engineer. 4 years of Python, SQL, and PostgreSQL.",
        "exp": 4.0,
    },
    {
        "name": "Eve Davis",
        "email": "eve@example.com",
        "text": "Full stack dev with React, Node.js, TypeScript and PostgreSQL. 5 years exp.",
        "exp": 5.0,
    },
    {
        "name": "Frank Evans",
        "email": "frank@example.com",
        "text": "ML Engineer. Python, AWS, and PyTorch. 3 years.",
        "exp": 3.0,
    },
    {
        "name": "Grace Hall",
        "email": "grace@example.com",
        "text": "Cloud Architect with 9 years in AWS, GCP, Docker, and Kubernetes.",
        "exp": 9.0,
    },
    {
        "name": "Harry Iles",
        "email": "harry@example.com",
        "text": "Go backend developer. 4 years Go, PostgreSQL, Docker.",
        "exp": 4.0,
    },
    {
        "name": "Ivy Johnson",
        "email": "ivy@example.com",
        "text": "Vue dev. 2 years Vue, JavaScript.",
        "exp": 2.0,
    },
    {
        "name": "Jack King",
        "email": "jack@example.com",
        "text": "Security engineer. 5 years Python, AWS.",
        "exp": 5.0,
    },
    {
        "name": "Kelly Lewis",
        "email": "kelly@example.com",
        "text": "React Native dev. 3 years React, JavaScript.",
        "exp": 3.0,
    },
    {
        "name": "Leo Martin",
        "email": "leo@example.com",
        "text": "Senior DevOps. 7 years AWS, Kubernetes.",
        "exp": 7.0,
    },
    {
        "name": "Mia Nelson",
        "email": "mia@example.com",
        "text": "Backend Python. 2 years Python, Django.",
        "exp": 2.0,
    },
    {
        "name": "Noah Owens",
        "email": "noah@example.com",
        "text": "Frontend TypeScript. 4 years TypeScript, React.",
        "exp": 4.0,
    },
    {
        "name": "Olivia Parker",
        "email": "olivia@example.com",
        "text": "Full stack. 6 years Python, React, PostgreSQL.",
        "exp": 6.0,
    },
]


async def seed():

    async with get_sessionmaker() as session:
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
