# ADR 0003: Aho-Corasick for Taxonomy Scanning

## Status
Accepted

## Context
We must scan unstructured resume text against a massive taxonomy of thousands of technical skills, frameworks, and job titles. Using sequential regex searches for each skill is highly inefficient and scales linearly with the dictionary size.

## Decision
We will use the Aho-Corasick automaton for simultaneous multi-pattern string search.

## Consequences
- **Positive:** Reduces scan time from $O(N \cdot M)$ (where $M$ is the number of skills and $N$ is text length) to $O(N + K)$ where $K$ is the number of matches. Scales exceptionally well with large taxonomies.
- **Negative:** Requires an upfront $O(\Sigma \cdot M)$ time and memory to build the deterministic finite automaton (trie + fail transitions). Requires memory optimization if the taxonomy grows too large.
