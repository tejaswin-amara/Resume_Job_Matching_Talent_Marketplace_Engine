# E2E Test Infrastructure & Architecture Specification

## 1. Overview & Dual-Track Methodology

The **E2E Testing Track** implements an independent, requirement-driven, opaque-box test framework for the Production-Grade Resume & Job Matching Talent Marketplace Engine. Designed according to the Project Pattern Dual Track, the test suite operates independently from internal implementation choices, evaluating the system strictly against explicit requirements defined in `ORIGINAL_REQUEST.md` and interface contracts in `PROJECT.md`.

### Core Architectural Principles
1. **Opaque-Box Independence**: Test cases assert external behavioral contracts (REST API status codes, RFC 7807 problem details, ATS mathematical formulas, flow conservation laws, Big-O scaling bounds, and zero-library constraints) without depending on private helper methods or mutable internal state.
2. **Progressive Testability**: The test harness is operable throughout all lifecycle milestones (M1 through M7). When live FastAPI servers or database instances are unavailable during early milestones, the harness seamlessly exercises the contract specifications using a high-fidelity reference engine; when backend services are active, it transparently dispatches to the live API.
3. **Deterministic Mathematical Oracles**: All scoring and algorithmic assertions derive expected values from formal specifications (e.g. ATS score formula `total = 100 * (0.40 * sem + 0.35 * skill + 0.15 * exp + 0.10 * edu)`, (1 + ln n) Greedy Set Cover approximation bounds, and flow conservation equations).

---

## 2. 4-Tier Test Strategy & Coverage Matrix

The suite is structured into 4 distinct tiers providing progressive depth from individual feature compliance to full user journeys:

| Tier | Name | Target Scope | Test Count | Execution File |
|---|---|---|---|---|
| **Tier 1** | **Feature Coverage** | Covers all individual features F01 through F35 in PROJECT.md Feature Inventory with >=5 tests per feature domain | 50 | `tests/e2e/test_tier1_features.py` |
| **Tier 2** | **Boundary & Corner Cases** | Zero-division resistance, empty/massive inputs, capacity bounds, disjoint sets, unicode, malformed files | 28 | `tests/e2e/test_tier2_boundaries.py` |
| **Tier 3** | **Cross-Feature Combinations** | Pairwise interactions: Parsing -> Aho-Corasick -> Scoring, Dinic Flow -> Explainability, Min-Cut -> Set Cover | 7 | `tests/e2e/test_tier3_combinations.py` |
| **Tier 4** | **Real-World Scenarios** | Multi-step end-to-end user workflows for candidates, recruiters, founders, and security verification | 5 | `tests/e2e/test_tier4_scenarios.py` |
| **Total** | | **Comprehensive E2E Opaque-Box Suite** | **90** | `tests/e2e/runner.py` |

---

## 3. Directory Layout & File Organization

```
tests/e2e/
├── __init__.py                     # Package initialization
├── conftest.py                     # Pytest session fixtures, markers, and golden datasets
├── runner.py                       # Standalone CLI test runner (--tier [1|2|3|4|all], --json-report)
├── test_tier1_features.py          # Tier 1: Feature Coverage (F01–F35)
├── test_tier2_boundaries.py        # Tier 2: Boundary & Corner Cases
├── test_tier3_combinations.py      # Tier 3: Cross-Feature Combinations
├── test_tier4_scenarios.py         # Tier 4: Real-World Application Scenarios
└── helpers/
    ├── __init__.py                 # Helper package initialization
    ├── assertions.py               # Domain assertions (ATS formula, RFC 7807, flow conservation, AST linter)
    ├── fixtures_data.py            # Golden datasets (5 candidates, 4 jobs, magic bytes, adversarial inputs)
    └── client.py                   # Unified client (live HTTP, Starlette TestClient, ReferenceContractEngine)
```

---

## 4. Test Execution Instructions

### A. Standalone Runner (`runner.py`)
The standalone runner provides a CLI interface with tier selection, verbose output, and structured JSON reporting:

```powershell
# Run all tiers (Tiers 1-4)
python tests/e2e/runner.py

# Run specific tier
python tests/e2e/runner.py --tier 1
python tests/e2e/runner.py --tier 2
python tests/e2e/runner.py --tier 3
python tests/e2e/runner.py --tier 4

# Run with verbose output
python tests/e2e/runner.py -v

# Run with keyword filter
python tests/e2e/runner.py -k "dinic"

# Generate JSON execution report
python tests/e2e/runner.py --json-report tests/e2e/report.json
```

### B. Standard Pytest
The test suite is fully integrated with `pytest`:

```powershell
# Run all E2E tests
python -m pytest tests/e2e

# Run with custom tier markers
python -m pytest tests/e2e -m tier1
python -m pytest tests/e2e -m tier2
python -m pytest tests/e2e -m tier3
python -m pytest tests/e2e -m tier4
```

### C. Live Backend Integration
To run against a live running FastAPI backend (e.g. running on Docker or uvicorn):

```powershell
$env:TEST_BACKEND_URL="http://localhost:8000"
python tests/e2e/runner.py
```

---

## 5. Domain Invariants & Verification Rules

1. **ATS Hybrid Scoring Invariant**:
   $$S_{\text{ATS}} = 100 \times (0.40 \cdot S_{\text{sem}} + 0.35 \cdot S_{\text{skill}} + 0.15 \cdot S_{\text{exp}} + 0.10 \cdot S_{\text{edu}})$$
   - Verified that $S_{\text{ATS}} \in [0.0, 100.0]$ and component scores $\in [0.0, 1.0]$.
   - Verified zero-division immunity on empty skill sets, 0 years required experience, and 0 education level.

2. **RFC 7807 Problem Details Standard**:
   - Error responses enforce `type`, `title`, `status`, `detail`, and `instance`.
   - Verified on 400 (empty file), 404 (non-existent requisition), 415 (unsupported media type), 422 (validation error).

3. **Network Flow Conservation Laws**:
   - $\sum_{\text{assigned}} \le \text{Capacity}_{\text{candidate}} = 1$
   - $\sum_{\text{assigned to job } j} \le \text{Capacity}_{\text{job } j}$
   - Total flow equals the number of matched pairs without overflow or cycle leakage.

4. **Greedy Set Cover Approximation Bound**:
   - For universe size $n$, the chosen team size satisfies:
     $$\text{Size} \le \lceil \text{OPT} \times (1 + \ln n) \rceil$$

5. **Cardinal Zero-Library Constraint**:
   - Verified via AST inspection in `assert_zero_library_compliance` that `core/engine/` contains zero forbidden imports (`collections`, `heapq`, `bisect`, `networkx`, `scipy`, `numpy`).
