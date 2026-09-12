#!/usr/bin/env python3
"""
Regenerates FULL-DOCUMENTATION.md by concatenating docs/*.md in section order.

This keeps the single-file version honest: FULL-DOCUMENTATION.md is never
hand-edited, it is always derived from docs/. Run this after any change to
a file in docs/, and commit the regenerated FULL-DOCUMENTATION.md alongside
your docs/ change.

Usage:
    python3 scripts/build_full_documentation.py
    python3 scripts/build_full_documentation.py --check   # CI mode: exits
                                                            # non-zero if the
                                                            # committed file
                                                            # is out of sync
"""
import argparse
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "docs"
OUTPUT = ROOT / "FULL-DOCUMENTATION.md"

HEADER = (
    "# Resume–Job Matching & Talent-Marketplace Engine\n"
    "## Full Engineering Documentation Package (single-file view)\n\n"
    "> Auto-generated from `docs/*.md` by `scripts/build_full_documentation.py`.\n"
    "> Do not hand-edit this file directly — edit the relevant file under "
    "`docs/` and regenerate.\n\n---\n\n"
)


def build() -> str:
    section_files = sorted(DOCS_DIR.glob("[0-9][0-9]-*.md"))
    if not section_files:
        raise SystemExit(f"No section files found under {DOCS_DIR}")
    parts = [HEADER]
    for f in section_files:
        parts.append(f.read_text(encoding="utf-8").rstrip() + "\n\n---\n\n")
    parts.append("*End of document.*\n")
    return "".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit 1 if FULL-DOCUMENTATION.md is not up to date (for CI)",
    )
    args = parser.parse_args()

    generated = build()

    if args.check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if current != generated:
            print(
                "FULL-DOCUMENTATION.md is out of sync with docs/. "
                "Run: python3 scripts/build_full_documentation.py",
                file=sys.stderr,
            )
            return 1
        print("FULL-DOCUMENTATION.md is up to date.")
        return 0

    OUTPUT.write_text(generated, encoding="utf-8")
    print(f"Wrote {OUTPUT} ({len(generated)} bytes) from {len(list(DOCS_DIR.glob('[0-9][0-9]-*.md')))} section files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
