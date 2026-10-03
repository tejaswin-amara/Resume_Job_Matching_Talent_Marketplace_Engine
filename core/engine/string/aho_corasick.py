"""AhoCorasickAutomaton: Multi-pattern dictionary matching automaton in O(N + M) time.

Zero-library constraint: built strictly with custom Trie nodes, array-based BFS,
and dictionary suffix links. Strictly no collections.deque.
"""

from typing import Any, NamedTuple


class AhoMatch(NamedTuple):
    """Result of an Aho-Corasick pattern match."""

    start: int
    end: int
    word: str
    payload: Any


class _AhoNode:
    """Trie node for Aho-Corasick automaton."""

    __slots__ = ("dict_link", "fail", "outputs", "transitions")

    def __init__(self) -> None:
        self.transitions: dict[str, _AhoNode] = {}
        self.fail: _AhoNode | None = None
        self.dict_link: _AhoNode | None = None
        self.outputs: list[tuple[str, Any]] = []


class AhoCorasickAutomaton:
    """Aho-Corasick automaton for simultaneous matching of 20,000+ keywords in a single linear pass."""

    def __init__(self, ignore_case: bool = False) -> None:
        self._root: _AhoNode = _AhoNode()
        self._is_built: bool = False
        self._word_count: int = 0
        self.ignore_case: bool = ignore_case

    @property
    def word_count(self) -> int:
        """Return total number of inserted patterns."""
        return self._word_count

    def add_word(self, word: str, payload: Any = None) -> None:
        """Insert a pattern word with optional payload metadata into the trie."""
        if not word:
            return

        self._is_built = False
        curr = self._root
        for char in word:
            key_char = char.lower() if self.ignore_case else char
            if key_char not in curr.transitions:
                curr.transitions[key_char] = _AhoNode()
            curr = curr.transitions[key_char]

        curr.outputs.append((word, payload))
        self._word_count += 1

    def build(self) -> None:
        """Construct failure links and dictionary output links via BFS.

        Uses a primitive array queue with head index to strictly obey zero-library constraint.
        """
        # Array-based BFS queue
        queue: list[_AhoNode] = []
        head = 0

        # Depth 1 nodes: failure link points to root
        for child in self._root.transitions.values():
            child.fail = self._root
            child.dict_link = None
            queue.append(child)

        # BFS level-by-level
        while head < len(queue):
            curr = queue[head]
            head += 1

            for char, child in curr.transitions.items():
                # Trace failure chain for the child
                f = curr.fail
                while f is not None and char not in f.transitions:
                    f = f.fail

                if f is not None and char in f.transitions:
                    child.fail = f.transitions[char]
                else:
                    child.fail = self._root

                # Dictionary output link optimization: point directly to nearest output node
                if child.fail.outputs:
                    child.dict_link = child.fail
                else:
                    child.dict_link = child.fail.dict_link

                queue.append(child)

        self._is_built = True

    def find_all(self, text: str) -> list[AhoMatch]:
        """Scan text and return all pattern occurrences in O(N + M) time.

        Each match returns AhoMatch(start=int, end=int, word=str, payload=Any).
        """
        if not self._is_built:
            self.build()

        matches: list[AhoMatch] = []
        curr = self._root

        for i, char in enumerate(text):
            key_char = char.lower() if self.ignore_case else char
            while curr is not None and key_char not in curr.transitions:
                curr = curr.fail

            if curr is None:
                curr = self._root
                continue

            curr = curr.transitions[key_char]

            # Collect outputs directly at current state
            temp: _AhoNode | None = curr
            while temp is not None:
                for word, payload in temp.outputs:
                    matches.append(
                        AhoMatch(
                            start=i - len(word) + 1,
                            end=i + 1,
                            word=word,
                            payload=payload,
                        )
                    )
                temp = temp.dict_link

        return matches

    def extract_keywords(self, text: str) -> list[str]:
        """Return list of distinct matched keyword strings in text."""
        matches = self.find_all(text)
        seen: set[str] = set()
        result: list[str] = []
        for m in matches:
            if m.word not in seen:
                seen.add(m.word)
                result.append(m.word)
        return result
