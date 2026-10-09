#!/bin/bash
set -e
echo "Running Ruff formatting and checks..."
uv run ruff check . --fix
uv run ruff format .

echo "Running Pytest..."
uv run pytest tests/

echo "Running Frontend checks..."
cd web
pnpm install
pnpm lint
pnpm test
pnpm exec playwright test
pnpm build
echo "All tests passed successfully!"
