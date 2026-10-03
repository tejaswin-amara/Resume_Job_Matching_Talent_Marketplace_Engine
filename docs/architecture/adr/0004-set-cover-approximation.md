# ADR 0004: Greedy Set Cover Approximation for Team Formation

## Status
Accepted

## Context
A recruiter wants to hire a "team" of candidates that collectively cover a required set of complementary skills (e.g., frontend, backend, devops, database). This is an instance of the Set Cover problem, which is NP-hard.

## Decision
We will implement a Greedy Set Cover Approximation algorithm to form candidate teams.

## Consequences
- **Positive:** The greedy approach runs in polynomial time and guarantees an approximation ratio of $H_n$ (where $n$ is the number of skills to cover, $H_n \approx \ln n$). It provides fast, interactive responses to the frontend.
- **Negative:** The solution is not strictly optimal; it may occasionally suggest a slightly larger team than the theoretical minimum, but this is acceptable in a real-world recruiting context where candidate overlap is beneficial.
