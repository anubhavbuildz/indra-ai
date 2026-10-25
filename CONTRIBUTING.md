# Contributing

Thanks for helping improve Indra. This is an early-stage backend project;
discuss substantial API, provider, schema, or Prowler-safety changes in an
issue before investing in a large implementation.

## Local setup

Use Python 3.12 or newer. From the repository root:

```bash
python -m pip install -e '.[dev]'
cp .env.example .env
```

The local app, tests, projects, and health endpoint do not require AWS or
NVIDIA credentials. Keep the placeholder `.env` values unchanged unless you
have a verified integration configuration.

## Changes and pull requests

- Create a focused branch from the current default branch.
- Explain the user-visible behavior, safety implications, and migration
  impact in the pull request.
- Include tests for changed behavior and update relevant documentation.
- Keep commits focused; do not commit local databases, FAISS artifacts,
  Prowler scan reports, generated credentials, or `.env`.
- Do not include secrets or cloud credentials in issues, pull requests,
  screenshots, logs, fixtures, or source files.
- Do not describe unperformed provider calls, compliance checks, or cloud
  deployments as successful.

## Style and checks

Use typed, maintainable Python and follow the existing service/repository
patterns. Run:

```bash
ruff check .
ruff format --check .
pytest --cov=app --cov-report=term-missing
```

For automatic formatting use `ruff format .`. Pre-commit hooks are available
with `pre-commit install`.

## Proposing changes

For a feature request, state the problem, smallest useful behavior, and
security/privacy effects. For a bug report, include a minimal reproduction
and redacted logs. Never attach credentials, Prowler reports, or sensitive
account data.
