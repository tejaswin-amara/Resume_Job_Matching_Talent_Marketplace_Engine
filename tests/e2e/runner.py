#!/usr/bin/env python3
"""Automated Test Runner for the E2E Opaque-Box Test Suite.

Supports:
- CLI flags for running individual tiers or all tiers (--tier [1|2|3|4|all])
- Pytest invocation and direct discovery
- JSON report generation (--json-report path)
- Rich terminal summary table and Big-O / feature matrix validation
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

# Ensure project root is in sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Requirement-Driven Opaque-Box E2E Tests (Tiers 1-4)",
    )
    parser.add_argument(
        "--tier",
        choices=["1", "2", "3", "4", "all"],
        default="all",
        help="Specify which test tier to execute (default: all)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "--json-report",
        type=str,
        default=None,
        help="Optional path to output execution results in JSON format",
    )
    parser.add_argument(
        "-k",
        "--keyword",
        type=str,
        default=None,
        help="Filter tests by keyword expression (passed to pytest -k)",
    )
    return parser.parse_args()


def run_tests(
    tier: str, verbose: bool, keyword: str | None = None, json_report: str | None = None
) -> int:
    import pytest

    test_dir = Path(__file__).resolve().parent

    pytest_args = ["-q"]
    if verbose:
        pytest_args.append("-vv")

    if tier == "1":
        pytest_args.append(str(test_dir / "test_tier1_features.py"))
    elif tier == "2":
        pytest_args.append(str(test_dir / "test_tier2_boundaries.py"))
    elif tier == "3":
        pytest_args.append(str(test_dir / "test_tier3_combinations.py"))
    elif tier == "4":
        pytest_args.append(str(test_dir / "test_tier4_scenarios.py"))
    else:
        pytest_args.append(str(test_dir))

    if keyword:
        pytest_args.extend(["-k", keyword])

    print("=" * 80)
    print("  PRODUCTION-GRADE TALENT MARKETPLACE — E2E OPAQUE-BOX TEST RUNNER")
    print("=" * 80)
    print(f"  Target Tier: {tier.upper()}")
    print(f"  Test Path  : {test_dir}")
    print(f"  Pytest Args: {' '.join(pytest_args)}")
    print("-" * 80)

    start_time = time.time()
    exit_code = pytest.main(pytest_args)
    elapsed = time.time() - start_time

    print("-" * 80)
    print(f"  Execution finished in {elapsed:.2f}s with exit code {exit_code}")
    print("=" * 80)

    if json_report:
        report_data = {
            "tier": tier,
            "exit_code": int(exit_code),
            "elapsed_seconds": elapsed,
            "status": "PASS" if exit_code == 0 else "FAIL",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        Path(json_report).parent.mkdir(parents=True, exist_ok=True)
        with open(json_report, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2)
        print(f"  JSON report written to: {json_report}")

    return int(exit_code)


if __name__ == "__main__":
    args = parse_args()
    code = run_tests(
        tier=args.tier,
        verbose=args.verbose,
        keyword=args.keyword,
        json_report=args.json_report,
    )
    sys.exit(code)
