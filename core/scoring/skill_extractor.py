from core.engine.dp.wagner_fischer import WagnerFischer
from core.engine.string.aho_corasick import AhoCorasickAutomaton


class SkillExtractor:
    """Extract skills from text using Aho-Corasick multi-pattern matching."""

    def __init__(self, skills: list[str] | None = None):
        if skills is None:
            skills = [
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
        self.skills = [s.lower() for s in skills]
        self.automaton = AhoCorasickAutomaton(ignore_case=True)
        for skill in self.skills:
            self.automaton.add_word(skill)
        self.automaton.build()
        self.wf = WagnerFischer()

    def extract(self, text: str) -> set[str]:
        """Extract all known skills from text using Aho-Corasick in O(N+M) time."""
        matches = self.automaton.find_all(text)
        return {match.word for match in matches}

    def fuzzy_match(self, word: str, threshold: int = 2) -> list[str]:
        """Find skills within edit distance threshold of the given word."""
        word = word.lower()
        return [
            skill
            for skill in self.skills
            if self.wf.levenshtein_distance(word, skill) <= threshold
        ]
