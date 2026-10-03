from core.scoring.matcher import HybridMatcher
from core.scoring.skill_extractor import SkillExtractor


def test_skill_extractor_finds_skills_via_aho_corasick():
    extractor = SkillExtractor(skills=["python", "java", "kubernetes"])
    skills = extractor.extract("I have 5 years of experience in Python and kubernetes.")
    assert "python" in skills
    assert "kubernetes" in skills
    assert "java" not in skills


def test_skill_extractor_fuzzy_match():
    extractor = SkillExtractor(skills=["javascript", "python"])
    matches = extractor.fuzzy_match("Javascritp", threshold=2)
    assert "javascript" in matches


def test_hybrid_matcher_score_formula():
    matcher = HybridMatcher()
    # sem=1.0, skill=1.0, exp=1.0, edu=1.0 => 100.0
    res = matcher.match([1.0], [1.0], {"python"}, {"python"}, 5.0, 3.0, "Bachelors", "Bachelors")
    assert res.total_score == 100.0


def test_hybrid_matcher_perfect_match():
    matcher = HybridMatcher()
    res = matcher.match(
        [1.0], [1.0], {"python", "java"}, {"python", "java"}, 5.0, 5.0, "masters", "masters"
    )
    assert res.total_score > 99.0


def test_hybrid_matcher_zero_skills():
    matcher = HybridMatcher()
    res = matcher.match([1.0], [1.0], set(), set(), 5.0, 5.0, "bachelors", "bachelors")
    assert res.skill_score == 1.0


def test_hybrid_matcher_zero_experience_requirement():
    matcher = HybridMatcher()
    res = matcher.match([1.0], [1.0], set(), set(), 0.0, 0.0, "bachelors", "bachelors")
    assert res.experience_score == 1.0


def test_hybrid_matcher_explainability_output():
    matcher = HybridMatcher()
    res = matcher.match(
        [1.0], [1.0], {"python"}, {"python", "java"}, 5.0, 5.0, "bachelors", "bachelors"
    )
    assert "python" in res.matched_skills
    assert "java" in res.missing_skills
    assert any("java" in s.lower() for s in res.suggestions)


def test_experience_score_overqualified():
    matcher = HybridMatcher()
    assert matcher.compute_experience_score(15.0, 3.0) == 1.0


def test_experience_score_underqualified():
    matcher = HybridMatcher()
    assert matcher.compute_experience_score(1.0, 10.0) == 0.0


def test_education_score_levels():
    matcher = HybridMatcher()
    # PhD > Masters > Bachelors > Associate > High School
    assert matcher.compute_education_score("PhD", "Masters") == 1.0
    assert matcher.compute_education_score("Masters", "PhD") == max(0.0, 1.0 - (5 - 4) * 0.25)
    assert matcher.compute_education_score("Bachelors", "Masters") == 0.75
    assert matcher.compute_education_score("Associate", "Masters") == 0.5
    assert matcher.compute_education_score("High School", "Masters") == 0.25
