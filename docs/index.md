# myproject

A Python project.

## Features

- Modern Python 3.12 and 3.13 with strict type checking
- Managed with [uv](https://docs.astral.sh/uv/) for fast, reliable dependency management
- Code quality enforced by [Ruff](https://docs.astral.sh/ruff/) and [mypy](https://mypy-lang.org/)
- Tested with [pytest](https://docs.pytest.org/), property-based testing via Hypothesis, and 100% coverage
- Pre-commit hooks for automated quality gates
- Docker support with multi-stage builds and functional HEALTHCHECK
- CI/CD via GitHub Actions — quality, test, security, and release pipelines
- GitHub issue templates, PR template, and CONTRIBUTING guide
- Documentation powered by [MkDocs Material](https://squidfunk.github.io/mkdocs-material/)

## Quick Start

```bash
# Clone and set up
git clone <repo-url> myproject
cd myproject

# Install development dependencies
uv sync --extra dev

# Run the project
uv run myproject

# Run all quality checks
make check
```

## Documentation

- [Getting Started](getting-started.md) - Setup, configuration, and development workflow
- [API Reference](api.md) - Auto-generated from source code
