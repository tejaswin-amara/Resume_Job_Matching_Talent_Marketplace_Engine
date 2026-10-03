# ADR 0002: Dinic's Algorithm for Network Flow Assignment

## Status
Accepted

## Context
We need to assign a pool of highly qualified candidates to multiple open job requisitions, optimizing for the best global fit. This can be modeled as a bipartite matching or network flow problem. The alternatives considered were the Hungarian algorithm and Dinic's algorithm.

## Decision
We chose Dinic's algorithm for maximum flow / bipartite matching assignment over the Hungarian algorithm.

## Consequences
- **Positive:** Dinic's algorithm efficiently handles bipartite matching in $O(E \sqrt{V})$ time, which scales better for sparse graphs formed by candidate-job preferences than the $O(V^3)$ Hungarian algorithm.
- **Negative:** Dinic's solves unweighted matching efficiently but requires modifications (like Min-Cost Max-Flow via Successive Shortest Path) if we introduce complex weighted preferences beyond thresholding.
