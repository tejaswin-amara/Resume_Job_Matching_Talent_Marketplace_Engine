# ADR 0001: Zero-Library Core for Algorithmic Engine

## Status
Accepted

## Context
The talent matching engine requires high-performance text parsing, fuzzy string matching, and combinatorial optimization for assigning candidates to jobs. We need to decide whether to use off-the-shelf Python libraries (like `networkx`, `ahocorasick`, `python-Levenshtein`) or implement these algorithms from scratch (zero-library constraint).

## Decision
We will implement the algorithmic core (Aho-Corasick, Dinic's, Wagner-Fischer) from scratch without external algorithmic libraries.

## Consequences
- **Positive:** Deep customizability, precise control over memory allocations, elimination of black-box dependency vulnerabilities, and easier integration of specific optimizations (e.g., parallel reductions).
- **Negative:** Increased initial development and maintenance overhead; requires comprehensive unit testing (77+ tests required) to ensure correctness.
