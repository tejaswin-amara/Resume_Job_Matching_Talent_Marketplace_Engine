"""GreedySetCover: (1 + ln n) approximation algorithm for minimal team competency formation.

Solves minimum-cost set cover to assemble a talent cohort covering all required job skills.
Zero-library constraint: built strictly on primitive sets and arrays.
"""

from typing import Sequence
from typing import Any, NamedTuple


class CandidateSkillProfile:
    """Represents a candidate's skill inventory and associated cost."""

    def __init__(
        self,
        candidate_id: Any,
        skills: Sequence[str],
        cost: float = 1.0,
    ) -> None:
        self.candidate_id: Any = candidate_id
        self.skills: set[str] = set(skills)
        self.cost: float = float(cost) if cost > 0 else 1.0

    def __repr__(self) -> str:
        return f"CandidateSkillProfile(id={self.candidate_id!r}, cost={self.cost}, skills={sorted(list(self.skills))})"


class TeamCoverResult(NamedTuple):
    """Result of minimum team composition approximation."""

    selected_candidates: list[CandidateSkillProfile]
    covered_skills: set[str]
    uncovered_skills: set[str]
    total_cost: float


class GreedySetCover:
    """Greedy set cover approximation engine with proven (1 + ln n) optimality ratio."""

    @classmethod
    def find_minimum_team(
        cls,
        candidates: Sequence[CandidateSkillProfile],
        target_skills: Sequence[str] | set[str],
    ) -> TeamCoverResult:
        """Find the minimal cost candidate cohort covering target_skills within (1 + ln |target_skills|)."""
        uncovered: set[str] = set(target_skills)
        covered: set[str] = set()
        selected: list[CandidateSkillProfile] = []
        total_cost: float = 0.0

        if not uncovered:
            return TeamCoverResult(
                selected_candidates=[],
                covered_skills=set(),
                uncovered_skills=set(),
                total_cost=0.0,
            )

        remaining_candidates: list[CandidateSkillProfile] = list(candidates)

        while uncovered and remaining_candidates:
            best_candidate: CandidateSkillProfile | None = None
            best_efficiency: float = -1.0  # newly covered skills per unit cost
            best_new_coverage: set[str] = set()

            for c in remaining_candidates:
                new_skills = c.skills & uncovered
                if new_skills:
                    efficiency = len(new_skills) / c.cost
                    if efficiency > best_efficiency:
                        best_efficiency = efficiency
                        best_candidate = c
                        best_new_coverage = new_skills

            if best_candidate is None or not best_new_coverage:
                # No remaining candidate can cover any more of uncovered skills
                break

            selected.append(best_candidate)
            remaining_candidates.remove(best_candidate)
            uncovered -= best_new_coverage
            covered |= best_new_coverage
            total_cost += best_candidate.cost

        return TeamCoverResult(
            selected_candidates=selected,
            covered_skills=covered,
            uncovered_skills=uncovered,
            total_cost=total_cost,
        )
