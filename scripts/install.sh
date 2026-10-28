#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3.12 or newer is required." >&2
  exit 1
fi

if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)'; then
  echo "Python 3.12 or newer is required." >&2
  exit 1
fi

if ! command -v node >/dev/null 2>&1 || ! command -v npm >/dev/null 2>&1; then
  echo "Node.js 20.19+ (or 22.12+) and npm are required." >&2
  exit 1
fi

if ! node -e 'const [major, minor] = process.versions.node.split(".").map(Number); process.exit(major >= 22 ? (major > 22 || minor >= 12 ? 0 : 1) : major === 20 && minor >= 19 ? 0 : 1)'; then
  echo "Node.js 20.19+ (or 22.12+) is required." >&2
  exit 1
fi

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env from .env.example; configure required values before using integrations."
fi

if [[ ! -f frontend/.env ]]; then
  cp frontend/.env.example frontend/.env
fi

.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e '.[dev]'
npm --prefix frontend ci
.venv/bin/alembic upgrade head

echo "Installation complete. See README.md for configuration and startup commands."
