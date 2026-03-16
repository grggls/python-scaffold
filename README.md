# myproject

[![CI](https://github.com/YOUR_USERNAME/myproject/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/myproject/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A Python project.

## Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/myproject.git
cd myproject

# Install dependencies
uv sync --extra dev

# Set up pre-commit hooks
uv run pre-commit install
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
myproject/
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
