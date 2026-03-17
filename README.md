# python-scaffold

[![CI](https://github.com/grggls/python-scaffold/actions/workflows/ci.yml/badge.svg)](https://github.com/grggls/python-scaffold/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A Python project scaffold with strict quality gates, 100% test coverage, and one-command project creation.

## Quick Start

Create a new project from this scaffold:

```bash
make new PROJECT=my_app
```

This clones the scaffold, runs the bootstrap renamer, initializes a git repo, creates a public GitHub repo, pushes, and configures branch protection — all in one step.

## Manual Setup

```bash
# Clone the repository
git clone https://github.com/grggls/python-scaffold.git my_app
cd my_app
rm -rf .git

# Rename the scaffold to your project name
python scripts/bootstrap.py my_app

# Initialize and push
git init && git add . && git commit -m "Initial commit"

# Install dependencies
make dev
```

## Usage

```bash
# Run the CLI
uv run myproject

# With verbose output
uv run myproject --verbose

# Show version
uv run myproject --version
```

## Development

```bash
# Run all quality checks (lint, format, typecheck, test)
make check

# Run tests with coverage
make test-cov

# Auto-format code
make format

# See all available commands
make help
```

## Project Structure

```
python-scaffold/
├── src/myproject/       # Package source code
│   ├── __init__.py      # Package version
│   ├── config.py        # Configuration from environment
│   ├── main.py          # CLI entry point
│   └── py.typed         # PEP 561 type marker
├── tests/               # Test suite
├── docs/                # Documentation source
├── .github/workflows/   # CI/CD pipeline
├── pyproject.toml       # Project configuration
├── Makefile             # Development commands
└── Dockerfile           # Container build
```

## Documentation

```bash
# Serve docs locally with live reload
make docs-serve

# Build static documentation
make docs-build
```

## Docker

```bash
# Build image
make docker-build

# Run container
make docker-run

# Development with docker-compose
docker-compose up
```

## License

[MIT](LICENSE)
