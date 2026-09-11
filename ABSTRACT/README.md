# Project Abstract

**Resume–Job Matching & Talent-Marketplace Engine**
Project report submitted for partial fulfilment of grade for **Data Structures and Algorithms – 3 (25CS2103E)**, A.Y. 2026-2027.

📄 Full submitted abstract: **[`DSA-3 Project Abstract.pdf`](<DSA-3 Project Abstract.pdf>)**

## Team

| | |
|---|---|
| **Team Number** | 36 |
| **Section** | 10 |
| **Guide** | Miss. Chandusha Kanda, Assistant Professor, CSIT |
| **Institution** | KL Deemed to be University, Hyderabad-500090, Telangana, India |

| Name | Roll Number |
|---|---|
| Tejaswin Amara | 2520090104 |
| Sai Ram Pragnay Murikipudi | 2520090081 |

## Summary

This project presents the design and implementation of a Resume–Job Matching and Talent-Marketplace Engine aimed at optimizing the recruitment pipeline. Modern hiring platforms must match large pools of resumes against job postings, normalize inconsistent skill vocabularies, assign candidates to roles optimally, and assemble minimal skill sets to staff teams.

To address this, the engine ingests and indexes textual data, using advanced string algorithms to parse and score candidate-to-job fit. It employs network-flow algorithms — bipartite matching — to compute the optimal assignment of candidates to available roles, maximizing placement efficiency. Finally, it applies approximation techniques to solve the NP-hard problem of determining the minimum skill set required to staff a given team.

Every core algorithm is hand-implemented (no standard-library collection/algorithm shortcuts), per the course's engine constraint — see the [top-level documentation](../README.md) for the full technical design.
