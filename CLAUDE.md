# myproject

## Project Overview
Python project using src/ layout, managed with uv, Python 3.12+.

## Validation Loop
After ANY code change, run this sequence. All must pass before a task is complete:
1. `uv run ruff check .` — lint
2. `uv run ruff format --check .` — format verification
3. `uv run mypy src/` — type checking (strict mode)
4. `uv run pytest` — tests

Shortcut: `make check` runs all four.

## Quick Commands
- `make check` — all quality gates
- `make test-cov` — tests with coverage report
- `make dev` — full development setup
- `make format` — auto-format code
- `make clean` — remove generated files

## Conventions
- Python 3.12 minimum, strict mypy, ruff for lint/format
- src/ layout: source in `src/myproject/`, tests in `tests/`
- All functions must have type annotations and return types
- All modules must have docstrings
- No TODO comments in delivered code
- Feature branches, conventional commits
- Line length: 100 characters
- Double quotes for strings

## Security Conventions
- Never hardcode secrets, API keys, or passwords — use environment variables
- Use `secrets` module for cryptographic randomness (not `random`)
- Never use `eval()`, `exec()`, or `pickle` with untrusted data
- Never disable SSL/TLS certificate verification
- Validate and sanitize all external input
- Log errors but never log secrets or PII
- Run `make audit` to check dependencies for known vulnerabilities

## Structure
- `src/myproject/` — package source code
- `tests/` — pytest test suite
- `docs/` — MkDocs documentation
- `scripts/` — utility scripts
- `.claude/commands/` — Claude Code slash commands

## Dependencies
- Managed via uv (`pyproject.toml`)
- Dev tools: ruff, mypy, pytest, pytest-cov, pytest-randomly, hypothesis, pip-audit, pre-commit, mkdocs-material, mkdocstrings
- Zero runtime dependencies by default
