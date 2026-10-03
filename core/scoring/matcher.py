class MatchResult:
    def __init__(
        self,
        semantic_score: float,
        skill_score: float,
        experience_score: float,
        education_score: float,
        total_score: float,
        matched_skills: list[str],
        missing_skills: list[str],
        suggestions: list[str],
    ):
        self.semantic_score = semantic_score
        self.skill_score = skill_score
        self.experience_score = experience_score
        self.education_score = education_score
        self.total_score = total_score
        self.matched_skills = matched_skills
        self.missing_skills = missing_skills
        self.suggestions = suggestions


class HybridMatcher:
    def __init__(self):
        pass

    def _dot_product(self, vec1: list[float], vec2: list[float]) -> float:
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        return sum(a * b for a, b in zip(vec1, vec2))

    def compute_semantic_score(self, cand_emb: list[float], job_emb: list[float]) -> float:
        # Assuming already L2 normalized
        score = self._dot_product(cand_emb, job_emb)
        return max(0.0, min(1.0, score))

    def compute_skill_score(
        self, cand_skills: set[str], job_skills: set[str]
    ) -> tuple[float, list[str], list[str]]:
        if not job_skills:
            return 1.0, list(cand_skills), []
        matched = cand_skills.intersection(job_skills)
        missing = job_skills.difference(cand_skills)
        score = len(matched) / len(job_skills)
        return score, list(matched), list(missing)

    def compute_experience_score(self, cand_exp: float, job_min_exp: float) -> float:
        if job_min_exp == 0:
            return 1.0
        if cand_exp >= job_min_exp:
            return 1.0

        # Calibrated 0-1 based on delta
        delta = job_min_exp - cand_exp
        if delta > 3.0:
            return 0.0

        return max(0.0, 1.0 - (delta / 3.0))

    def compute_education_score(self, cand_edu: str, job_req_edu: str) -> float:
        levels = {"high school": 1, "associate": 2, "bachelors": 3, "masters": 4, "phd": 5}
        c_val = levels.get(cand_edu.lower(), 0)
        j_val = levels.get(job_req_edu.lower(), 0)
        if j_val == 0:
            return 1.0
        if c_val >= j_val:
            return 1.0
        return max(0.0, 1.0 - (j_val - c_val) * 0.25)

    def match(
        self,
        cand_emb: list[float],
        job_emb: list[float],
        cand_skills: set[str],
        job_skills: set[str],
        cand_exp: float,
        job_min_exp: float,
        cand_edu: str = "",
        job_req_edu: str = "",
    ) -> MatchResult:

        sem = self.compute_semantic_score(cand_emb, job_emb)
        skill_score, matched, missing = self.compute_skill_score(cand_skills, job_skills)
        exp = self.compute_experience_score(cand_exp, job_min_exp)
        edu = self.compute_education_score(cand_edu, job_req_edu)

        total = 100.0 * (0.40 * sem + 0.35 * skill_score + 0.15 * exp + 0.10 * edu)

        suggestions = []
        if missing:
            suggestions.append(f"Consider learning: {', '.join(missing[:3])}")

        return MatchResult(sem, skill_score, exp, edu, total, matched, missing, suggestions)
