# Getting Started

Complete reference for every tool, file, technique, and design decision in this scaffold.

## Prerequisites

### Python 3.12+

This project requires Python 3.12 or later. Python 3.12 brings improved error messages with
precise locations, type parameter syntax (PEP 695), and f-string improvements that remove
previous limitations.

Check your version:

```bash
python --version
```

### uv Package Manager

[uv](https://docs.astral.sh/uv/) is a Rust-based Python package manager that replaces pip,
venv, pip-tools, and pyenv in a single tool. It is chosen over pip/poetry because:

- **Speed**: 10-100x faster than pip for dependency resolution and installation
- **Lockfiles**: Generates `uv.lock` for reproducible builds across environments
- **Python version management**: Can install and manage Python versions directly
- **Standards-compliant**: Uses `pyproject.toml` (PEP 621) as the single source of truth
- **Replaces multiple tools**: pip + venv + pip-tools + pyenv in one binary

Install uv:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Docker (Optional)

Required only for containerized deployment. Install from
[docker.com](https://docs.docker.com/get-docker/).

### direnv (Optional)

[direnv](https://direnv.net/) automatically activates your virtual environment when you `cd`
into the project directory. Install via your package manager:

```bash
brew install direnv    # macOS
apt install direnv     # Debian/Ubuntu
```

---

## Quick Start

### One-Command Setup (Recommended)

From an existing clone of the scaffold:

```bash
make new PROJECT=my_app
```

This single command:

1. Clones the scaffold into `../my_app/`
2. Removes the scaffold's git history
3. Runs the bootstrap renamer (converts hyphens to underscores for Python)
4. Initializes a fresh git repo with an initial commit
5. Creates a public GitHub repo and pushes
6. Installs dev dependencies and pre-commit hooks (`make dev`)
7. Configures branch protection on `main` (PRs required, no force push)

The bootstrap step prompts for author name, email, and GitHub username — press Enter to accept the defaults.

### Manual Setup

```bash
# 1. Clone the scaffold
git clone https://github.com/grggls/python-scaffold.git my_app
cd my_app
rm -rf .git

# 2. Rename the project (prompts for name, author, email, GitHub username)
python scripts/bootstrap.py my_app

# 3. Initialize and commit
git init
git add .
git commit -m "Initial commit"

# 4. Install development dependencies
make dev

# 5. Verify everything works
make check
```

### Day-to-Day Development

```bash
# Run the project
uv run myproject

# Run with verbose output
uv run myproject --verbose

# Run all quality checks before pushing
make check

# Run tests with coverage
make test-cov

# Format code
make format

# Serve documentation locally
make docs-serve
```

---

## Project Structure Explained

### `pyproject.toml` — Single Source of Truth

The central configuration file. Replaces the legacy combination of `setup.py`, `setup.cfg`,
`requirements.txt`, and `tox.ini`. Every tool reads its configuration from this one file.
See the [pyproject.toml Deep Dive](#pyprojecttoml-deep-dive) section below.

### `src/myproject/` — Source Layout

The project uses the **src layout** where package code lives under `src/`. This is the
[PyPA-recommended](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)
approach because:

- **Prevents accidental imports**: You cannot accidentally import your package without
  installing it first. This catches packaging bugs early.
- **Tests run against the installed package**: Ensures your tests validate the same code
  your users will install.
- **Clear separation**: Source code, tests, docs, and scripts each have their own top-level
  directory.

### `src/myproject/__init__.py` — Package Identity

Contains the package docstring and `__version__` string. The version is the single source of
truth for the package version, importable as `myproject.__version__`.

### `src/myproject/py.typed` — PEP 561 Marker

An empty file that tells type checkers (mypy, Pyright, Pyre) that this package ships inline
type annotations. Without this marker, type checkers may ignore your type hints when your
package is used as a dependency. PEP 561 defines the standard for distributing type
information in Python packages.

### `src/myproject/config.py` — Configuration Module

Loads application settings from environment variables using stdlib `dataclasses`. The
`@dataclass(frozen=True)` decorator makes settings immutable after creation, preventing
accidental modification at runtime.

`__post_init__` validates `LOG_LEVEL` against the set of known Python logging levels
(`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`). An invalid value raises `ValueError`
with a clear message at startup rather than failing silently or crashing deep in the logging
machinery.

Uses stdlib instead of pydantic-settings to keep the scaffold at zero runtime dependencies.
To upgrade to pydantic-settings later:

1. Add `pydantic-settings` to `[project.dependencies]`
2. Change the dataclass to `class Settings(BaseSettings)`
3. Remove the manual `os.environ.get()` calls

### `src/myproject/main.py` — CLI Entry Point

The command-line interface, registered in `pyproject.toml` under `[project.scripts]` as:

```toml
[project.scripts]
myproject = "myproject.main:main"
```

When the package is installed (via `uv sync`), this creates an executable `myproject` command
that calls the `main()` function. The function returns an integer exit code (0 = success).

### `tests/` — Test Suite

All tests live in the `tests/` directory, separate from source code. Tests are discovered by
pytest based on the `testpaths = ["tests"]` setting in `pyproject.toml`.

### `tests/conftest.py` — Shared Fixtures

pytest automatically loads `conftest.py` files and makes their fixtures available to all
tests in the same directory and below. Fixtures are reusable setup/teardown functions
decorated with `@pytest.fixture`. They replace the `setUp`/`tearDown` pattern from
`unittest` with a more flexible dependency injection approach.

### `docs/` — Documentation Source

Markdown files for MkDocs. Edit these to update your project documentation. The `mkdocs.yml`
configuration file maps these files to the navigation structure.

### `scripts/bootstrap.py` — One-Time Rename Tool

A stdlib-only Python script that renames `myproject` to your chosen project name across all
files and directories. Run once after cloning the scaffold, then optionally delete it.

It prompts for four values (defaults shown in brackets):

| Prompt | Default | Replaces |
| --- | --- | --- |
| Project name | *(required)* | `myproject` / `MyProject` / `MYPROJECT` |
| Author name | `Gregory Damiani` | Author in `pyproject.toml` and docs |
| Author email | `gregory.damiani@gmail.com` | Email in `pyproject.toml` and docs |
| GitHub username | `grggls` | GitHub references in URLs and badges |

### `.claude/` — Claude Code Configuration

Project-level configuration for the Claude Code AI assistant. Contains tool permissions,
slash commands, and the validation loop. See
[Claude Code Integration](#claude-code-integration) below.

---

## pyproject.toml Deep Dive

### `[build-system]`

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

Declares the build backend per PEP 517/518. **hatchling** is chosen because:

- Default backend for uv-initialized projects
- Lightweight with minimal opinions
- Standards-compliant (PEP 517/518/621)
- Handles src layout automatically

### `[project]`

```toml
[project]
name = "myproject"
version = "0.1.0"
description = "A Python project."
requires-python = ">=3.12"
```

PEP 621 standard metadata. All fields are read by packaging tools, PyPI, and downstream
users. `requires-python` ensures installation fails on older Python versions rather than
producing cryptic errors.

### `[project.scripts]`

```toml
[project.scripts]
myproject = "myproject.main:main"
```

Maps a command name to a `module:function` path. When installed, `uv` creates an executable
script in the virtualenv's `bin/` directory. The function must be callable with no required
arguments and should return an integer exit code.

### `[project.optional-dependencies]`

```toml
[project.optional-dependencies]
dev = [
    "hypothesis>=6.100",
    "mypy>=1.10",
    "mkdocs-material>=9.5",
    "mkdocstrings[python]>=0.25",
    "pip-audit>=2.7",
    "pre-commit>=3.7",
    "pytest>=8.2",
    "pytest-cov>=5.0",
    "pytest-randomly>=3.15",
    "ruff>=0.5",
]
```

Development dependencies that are not needed at runtime. Install with `uv sync --extra dev`.
This keeps your production installation lean — users of your package never install pytest or
ruff. Security tools (`pip-audit`, `hypothesis`, `pytest-randomly`) are included here to
ensure they are available in every development environment.

### `[tool.ruff]`

```toml
[tool.ruff]
line-length = 100
target-version = "py312"
```

- **line-length = 100**: Wider than PEP 8's 79 characters. Modern screens and editors can
  comfortably display 100-character lines, reducing artificial line breaks that hurt
  readability.
- **target-version = "py312"**: Enables Python 3.12-specific lint rules and formatting. Ruff
  will suggest modern syntax where available (e.g., `match` statements, type parameter
  syntax).

### `[tool.ruff.lint]`

```toml
[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "S", "B"]
```

Each letter code enables a set of rules:

| Code | Source | What It Checks |
|------|--------|---------------|
| `E` | pycodestyle | Style errors (whitespace, indentation, line length) |
| `F` | pyflakes | Logical errors (undefined names, unused imports, redefined variables) |
| `I` | isort | Import ordering (stdlib, third-party, first-party grouping) |
| `N` | pep8-naming | Naming conventions (ClassName, function_name, CONSTANT_NAME) |
| `W` | pycodestyle | Style warnings (deprecated features, trailing whitespace) |
| `UP` | pyupgrade | Modernize syntax (f-strings over .format(), modern type hints) |
| `S` | flake8-bandit | Security issues (eval, hardcoded passwords, unsafe deserialization) |
| `B` | flake8-bugbear | Bug-prone patterns (mutable defaults, broad exceptions) |

### `[tool.ruff.lint.isort]`

```toml
[tool.ruff.lint.isort]
known-first-party = ["myproject"]
```

Tells the import sorter which packages are part of your project. Without this, imports from
`myproject` might be sorted as third-party packages.

### `[tool.ruff.format]`

```toml
[tool.ruff.format]
quote-style = "double"
```

Enforces double quotes throughout the project for consistency. Ruff's formatter is a
drop-in replacement for Black with identical output.

### `[tool.mypy]`

```toml
[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true
```

- **strict = true**: Enables all optional strictness flags at once. This means:
    - No implicit `Any` types allowed
    - All function definitions must have type annotations
    - Return types are checked against annotations
    - Missing imports are reported as errors
- **warn_return_any**: Warns when a function annotated with a specific return type actually
  returns `Any`
- **warn_unused_configs**: Warns if mypy configuration options have no effect

### `[tool.pytest.ini_options]`

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra -q"
```

- **testpaths**: Tells pytest to look for tests only in the `tests/` directory
- **addopts = "-ra -q"**: Default flags for every pytest run:
    - `-r a`: Show extra summary info for **a**ll test outcomes except passed
    - `-q`: Quiet output (less verbose, one line per test file)

### `[tool.coverage.run]`

```toml
[tool.coverage.run]
source = ["src/myproject"]
branch = true
```

- **source**: Only measure coverage for your project code, not dependencies
- **branch = true**: Enables branch coverage, which checks whether both sides of `if/else`,
  `try/except`, and other branching constructs are tested. Line coverage alone can miss
  untested branches.

### `[tool.coverage.report]`

```toml
[tool.coverage.report]
show_missing = true
fail_under = 100
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "if __name__",
]
```

- **show_missing = true**: Shows exact line numbers that lack test coverage
- **fail_under = 100**: The test suite fails if coverage drops below 100%. This ensures
  every line and branch is tested.
- **exclude_lines**: Lines matching these patterns are excluded from coverage measurement:
    - `pragma: no cover`: Explicit opt-out for specific lines
    - `if TYPE_CHECKING:`: Import blocks only used by type checkers, never executed at
      runtime
    - `if __name__`: Script entry point guard, tested separately

---

## Makefile Targets Reference

Run `make help` to see all available targets. Every target is documented below.

| Target | Command | When to Use |
|--------|---------|-------------|
| `make help` | *(self-documenting)* | See all available targets with descriptions |
| `make install` | `uv sync` | Install production dependencies only |
| `make dev` | `uv sync --extra dev && uv run pre-commit install` | First-time setup or after changing dev dependencies |
| `make test` | `uv run pytest` | Quick test run during development |
| `make test-cov` | `uv run pytest --cov --cov-report=term-missing --cov-report=html` | Detailed coverage analysis. Opens `htmlcov/index.html` for visual report |
| `make lint` | `uv run ruff check .` | Check for linting violations without auto-fixing |
| `make format` | `uv run ruff format . && uv run ruff check --fix .` | Auto-format all Python files and fix safe lint violations |
| `make format-check` | `uv run ruff format --check .` | Verify formatting without changes (used in CI) |
| `make typecheck` | `uv run mypy src/` | Static type analysis in strict mode |
| `make check` | lint + format-check + typecheck + test | Run ALL quality gates. Use before pushing. Mirrors CI. |
| `make clean` | `rm -rf` caches and artifacts | Remove all generated files (`__pycache__`, `.coverage`, `htmlcov/`, `dist/`, `build/`, `site/`) |
| `make build` | `uv build` | Build sdist and wheel into `dist/` for publishing |
| `make docker-build` | `docker build -t myproject:latest .` | Build production Docker image |
| `make docker-run` | `docker run --rm myproject:latest` | Run the Docker container |
| `make docs-serve` | `uv run mkdocs serve` | Live-preview docs at `localhost:8000` with auto-reload |
| `make docs-build` | `uv run mkdocs build` | Build static documentation site into `site/` |
| `make audit` | `uv run pip-audit` | Scan dependencies for known vulnerabilities (CVEs) |
| `make bootstrap` | `python scripts/bootstrap.py` | Rename project after cloning scaffold (one-time) |
| `make new` | clone + bootstrap + git init + gh repo create | Create a new project from the scaffold in one step. Usage: `make new PROJECT=my_app` |

### Typical Development Workflow

```bash
# 1. Set up (once)
make dev

# 2. Write code and tests

# 3. Format and check
make format
make check

# 4. Before pushing
make check  # runs lint + format-check + typecheck + test
```

---

## Pre-Commit Hooks Reference

Pre-commit hooks run automatically on every `git commit`. If any hook fails, the commit is
blocked. Some hooks auto-fix issues — when that happens, re-stage the fixed files with
`git add` and commit again.

### Installation

```bash
uv run pre-commit install
```

### Manual Run (All Files)

```bash
uv run pre-commit run --all-files
```

### Hook Reference

#### Guard Rails (pre-commit-hooks)

| Hook | What It Does |
|------|-------------|
| `check-ast` | Validates that Python files parse correctly. Catches syntax errors before commit. |
| `check-yaml` | Validates YAML file syntax (CI workflows, docker-compose, mkdocs config). |
| `check-toml` | Validates TOML file syntax. Catches `pyproject.toml` errors. |
| `check-merge-conflict` | Prevents committing files with unresolved merge conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`). |
| `trailing-whitespace` | Strips trailing whitespace from all lines. **Auto-fixes**. |
| `end-of-file-fixer` | Ensures every file ends with exactly one newline. **Auto-fixes**. |
| `check-added-large-files` | Prevents accidentally committing large binary files (images, data files, compiled artifacts). |

#### Code Quality (Ruff)

| Hook | What It Does |
|------|-------------|
| `ruff` (with `--fix`) | Runs all configured lint rules (E, F, I, N, W, UP, S, B). **Auto-fixes** safe violations like import sorting and unused imports. |
| `ruff-format` | Formats code consistently (replaces Black). Enforces line length, quote style, indentation. **Auto-fixes**. |

#### Type Safety (mypy)

| Hook | What It Does |
|------|-------------|
| `mypy` (with `--strict`) | Static type analysis. Catches type errors, missing annotations, implicit `Any` types. Does not auto-fix — you must correct type issues manually. |

#### Security (gitleaks)

| Hook | What It Does |
|------|-------------|
| `gitleaks` | Scans staged files for accidentally committed secrets: API keys, passwords, tokens, private keys. Blocks the commit if secrets are detected. |

### When Hooks Auto-Fix

Some hooks modify files automatically:

1. `trailing-whitespace` removes trailing spaces
2. `end-of-file-fixer` adds missing final newlines
3. `ruff --fix` fixes safe lint violations (import sorting, unused imports)
4. `ruff-format` reformats code

When this happens:

```bash
# Hook auto-fixed files, commit was blocked
git add -u          # Re-stage the auto-fixed files
git commit          # Try again — should pass now
```

---

## Claude Code Integration

This scaffold includes project-level configuration for [Claude Code](https://claude.com/claude-code),
an AI coding assistant.

### CLAUDE.md — Validation Loop

The `CLAUDE.md` file at the project root contains instructions that Claude reads at the start
of every session. The most important section is the **validation loop**:

After ANY code change, Claude runs these four commands in order:

1. `uv run ruff check .` — Lint check
2. `uv run ruff format --check .` — Format verification
3. `uv run mypy src/` — Type checking
4. `uv run pytest` — Tests

All four must pass before Claude considers a task complete. This ensures every change
maintains code quality.

### `.claude/settings.json` — Tool Permissions

Pre-configures which shell commands Claude can run without prompting you for each one:

- `uv *` — Package management
- `make *` — Makefile targets
- `pytest *` — Test runner
- `ruff *` — Linter/formatter
- `mypy *` — Type checker
- `python scripts/*` — Project scripts
- `docker *`, `docker-compose *` — Containerization
- `mkdocs *` — Documentation
- `pre-commit *` — Git hooks
- `git *` — Version control

### `.claude/commands/` — Slash Commands

Custom commands you can invoke in Claude Code:

| Command | What It Does |
|---------|-------------|
| `/check` | Runs all 4 quality gates and reports PASS/FAIL for each |
| `/test` | Runs pytest with coverage and reports summary |
| `/bootstrap` | Guides you through renaming the scaffold project |

### Best Practices with Claude Code

1. **Start in Plan Mode**: Before implementing, ask Claude to plan its approach
2. **Use `/check` often**: After significant changes, verify all gates pass
3. **Clear between features**: Use `/clear` to reset context between unrelated tasks
4. **Interrupt early**: If Claude goes off track, press Escape and redirect
5. **Let Claude maintain CLAUDE.md**: Ask Claude to update rules as conventions evolve

---

## Docker Setup

### Multi-Stage Build

The `Dockerfile` uses a two-stage build:

**Stage 1 — Builder**: Installs uv and all dependencies into a virtual environment.

**Stage 2 — Runtime**: Copies only the virtual environment and source code. The builder's
tools (uv, pip, compilers) are not included, resulting in a smaller, more secure image.

### Non-Root User

The container runs as `appuser` instead of `root`. This is a security best practice — if the
application is compromised, the attacker cannot modify system files or install software.

### `.dockerignore`

Excludes unnecessary files from the Docker build context:

- Tests, docs, scripts — not needed in production
- `.git`, `.github`, `.claude` — development-only
- Caches, coverage reports — build artifacts
- `.env` files — secrets should be injected via environment variables, not baked into images

### docker-compose.yml

Development environment with:

- Environment file (`.env`) for local configuration
- Commented-out examples for PostgreSQL and Redis — uncomment when needed

### Commands

```bash
# Build the image
make docker-build

# Run the container
make docker-run

# Development with docker-compose
docker-compose up
```

---

## CI/CD Pipeline

### GitHub Actions Workflow (`.github/workflows/ci.yml`)

Triggers on:

- **Push to `main`**: Validates that the main branch stays clean
- **Pull requests to `main`**: Validates changes before merging

### Three-Job Pipeline

Both `quality` and `test` jobs run a **Python 3.12 × 3.13 matrix**, ensuring the code works
on all supported interpreter versions.

**Job 1 — `quality`** (matrix: 3.12, 3.13): Fast checks that catch most issues:

- Lint (`ruff check`) — including S (security) and B (bugbear) rules
- Format verification (`ruff format --check`)
- Type checking (`mypy src/`)

**Job 2 — `test`** (matrix: 3.12, 3.13; depends on `quality`): Only runs if quality passes:

- Full test suite with coverage (`pytest --cov`)
- Coverage report uploaded to Codecov (3.12 only, to avoid duplicate uploads)

**Job 3 — `security`** (runs independently): Security-specific checks:

- Semgrep SAST — taint-tracking and data-flow analysis
- pip-audit — dependency CVE scanning

The pipeline is split into three jobs. Quality checks are fast (~5 seconds) and catch most
issues. Tests only run when code quality is verified. Security scans run independently so
they are never skipped even if tests fail.

### Release Pipeline (`.github/workflows/release.yml`)

Triggers on a version tag push (`v*.*.*`). Runs the full quality gate, builds the wheel and
sdist via `uv build`, then publishes to PyPI using
[trusted publishing](https://docs.pypi.org/trusted-publishers/) (OIDC — no API token
needed). Requires a `release` GitHub Actions environment configured in repository settings.

To release:

```bash
git tag v1.0.0
git push origin v1.0.0
```

### Dependabot (`.github/dependabot.yml`)

Automatically opens pull requests when dependencies have updates:

- **pip**: Weekly checks for Python package updates
- **github-actions**: Weekly checks for Action version updates

Each type is limited to 5 open PRs to avoid overwhelming your PR queue.

### Permissions

The workflow uses `permissions: contents: read` (least privilege). It can read your code but
cannot push, create releases, or modify repository settings.

---

## Configuration & Environment

### `.env.example`

Template showing all environment variables the application reads. Copy to `.env` for local
development:

```bash
cp .env.example .env
```

The `.env` file is gitignored — it should never be committed because it may contain secrets.
The `.env.example` file is committed as documentation of available settings.

### `.envrc`

[direnv](https://direnv.net/) configuration. When you `cd` into the project directory,
direnv automatically activates the virtual environment. Run `direnv allow` once to trust the
file.

### `.editorconfig`

Ensures consistent coding style across different editors and IDEs:

- **Python files**: 4-space indentation (PEP 8)
- **YAML/JSON/TOML**: 2-space indentation (convention)
- **Makefile**: Tab indentation (required by `make`)
- **All files**: UTF-8 encoding, LF line endings, trailing newline

Most editors support `.editorconfig` natively or via plugins.

---

## Documentation System

### MkDocs with Material Theme

[MkDocs](https://www.mkdocs.org/) generates a static documentation site from Markdown
files. The [Material theme](https://squidfunk.github.io/mkdocs-material/) adds:

- Light/dark mode toggle
- Search functionality
- Code syntax highlighting with copy buttons
- Tabbed content blocks
- Admonition (callout) blocks

### mkdocstrings

The [mkdocstrings](https://mkdocstrings.github.io/) plugin auto-generates API reference
documentation from Python docstrings. In Markdown files, use:

```markdown
::: myproject.main
```

This renders the module's classes, functions, and their docstrings as formatted documentation.

### Commands

```bash
# Live preview with auto-reload
make docs-serve
# Opens at http://localhost:8000

# Build static site
make docs-build
# Output in site/ directory
```

---

## Security

This scaffold enforces security at multiple layers: static analysis catches issues in code
before it runs, dynamic analysis catches issues at runtime during testing, and dependency
scanning catches known vulnerabilities in third-party packages.

### Static Analysis

#### Ruff Security Rules (`S` — Bandit)

The `S` rule set is ruff's built-in reimplementation of
[Bandit](https://bandit.readthedocs.io/), the Python security linter. These rules catch
common security anti-patterns at the code level:

| Rule | What It Catches |
|------|----------------|
| `S101` | `assert` used outside tests (assertions are stripped in optimized mode) |
| `S104` | Binding to `0.0.0.0` (exposes service to all network interfaces) |
| `S105`–`S107` | Hardcoded passwords, secrets, or temporary file paths |
| `S301`–`S303` | Unsafe deserialization (`pickle`, `marshal`) and weak hashes (`MD5`, `SHA1`) |
| `S307` | Use of `eval()` (arbitrary code execution) |
| `S324` | Insecure hash functions for security purposes |
| `S501`–`S506` | Disabled SSL/TLS verification |
| `S608` | SQL injection via string formatting |
| `S701` | Jinja2 templates with autoescape disabled (XSS risk) |

Tests are allowed to use `assert` statements, so `S101` is suppressed for test files via
per-file-ignores in `pyproject.toml`:

```toml
[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101"]
```

**Handling false positives**: Add `# noqa: S101` (or the relevant rule code) to suppress a
specific line. Use sparingly and always add a comment explaining why the suppression is safe.

#### Ruff Bugbear Rules (`B`)

The `B` rule set catches Python bugs that often have security implications:

| Rule | What It Catches |
|------|----------------|
| `B006` | Mutable default arguments (shared state between calls) |
| `B007` | Unused loop variables (may indicate logic errors) |
| `B008` | Function calls in default arguments (evaluated once at import time) |
| `B009`–`B010` | Use of `getattr`/`setattr` with constant attributes |
| `B017` | `assertRaises(Exception)` — too broad, hides real errors |

#### Semgrep SAST in CI

[Semgrep](https://semgrep.dev/) provides **taint-tracking** and **data-flow analysis** that
pattern-based tools like ruff cannot do. While ruff catches patterns (using `eval()`),
Semgrep traces untrusted data through function calls to detect injection vulnerabilities.

For example, Semgrep can detect that user input flows through three function calls into a
SQL query — something a pattern matcher cannot see.

Semgrep runs in CI only (no local install needed) with the `auto` config, which uses
curated Python security rules with low false positive rates. The scan takes about 5–10
seconds.

#### mypy Strict Mode

Strict type checking is a security tool: `strict = true` prevents implicit `Any` types,
which can hide untrusted data flowing through your code without validation. When every
value has a known type, it is harder for malicious input to bypass type-based validation.

### Dynamic Analysis

#### pytest-randomly — Test Order Randomization

[pytest-randomly](https://github.com/pytest-dev/pytest-randomly) randomizes test execution
order on every run. This catches:

- **Hidden test coupling**: Test A passes only because Test B ran first and set up shared
  state
- **Shared mutable state**: Tests that accidentally share data between runs
- **Setup/teardown bugs**: Initialization issues that only appear in certain orderings

Zero configuration — auto-enabled when installed. Seeds are printed so failures are
reproducible:

```
Using --randomly-seed=1234567
```

To reproduce a specific order:

```bash
uv run pytest --randomly-seed=1234567
```

#### Hypothesis — Property-Based Testing

[Hypothesis](https://hypothesis.readthedocs.io/) generates hundreds of random inputs per
test run, catching edge cases that manual tests miss:

- Empty strings, unicode characters, null bytes, extremely long strings
- Boundary values, special characters, encoding issues
- Combinations that humans rarely think to test

The scaffold includes one example property-based test as a **pattern to follow**:

```python
from hypothesis import given, strategies as st

@given(st.text())
def test_settings_app_name_accepts_any_string(self, name: str) -> None:
    settings = Settings(app_name=name)
    assert settings.app_name == name
```

Use Hypothesis when writing validation-heavy code, parsers, or data transformations. It is
not mandatory for every test — use it where input variety matters.

#### How Static + Dynamic Complement Each Other

Static analysis catches **code patterns** (using `eval()`, hardcoded passwords) but cannot
reason about runtime behavior. Dynamic analysis catches **logic bugs** (test coupling,
unexpected input handling) but only tests paths that are actually executed. Together, they
cover both classes of defects.

### Dependency Security

#### pip-audit — CVE Scanning

[pip-audit](https://github.com/pypa/pip-audit) scans your installed packages against the
[OSV](https://osv.dev/) database of known vulnerabilities (CVEs). Run locally:

```bash
make audit
```

When vulnerabilities are found:

1. Check the advisory for severity and affected versions
2. Update the vulnerable package: `uv add 'package>=fixed_version'`
3. Run `make audit` again to verify
4. If no fix is available, assess the risk and document the decision

pip-audit also runs in CI on every push and pull request.

#### Dependabot — Automatic Dependency Updates

GitHub Dependabot automatically opens pull requests when dependencies have updates. This
includes security patches — Dependabot monitors the GitHub Advisory Database and creates
PRs with urgency labels for security fixes.

Review Dependabot PRs by checking the changelog and running `make check` on the branch.

#### `uv.lock` — Supply Chain Protection

Committing `uv.lock` prevents supply chain attacks:

- **Dependency confusion**: An attacker publishes a malicious package with the same name on
  a public registry. The lockfile pins exact versions and hashes.
- **Typosquatting**: Packages with names similar to popular libraries. The lockfile ensures
  you always install the exact package you resolved during development.
- **Reproducible builds**: Everyone installs identical versions, eliminating "it works on my
  machine" issues that can mask security problems.

### Secrets & Configuration Security

#### gitleaks — Pre-Commit Secret Scanning

The [gitleaks](https://github.com/gitleaks/gitleaks) pre-commit hook scans every staged
file for patterns matching API keys, passwords, tokens, and private keys. If a secret is
detected, the commit is blocked.

Common patterns detected: AWS keys, GitHub tokens, Slack tokens, private keys (RSA, DSA,
EC), generic passwords and API key patterns.

**Handling false positives**: Create a `.gitleaksignore` file with the fingerprint of the
allowed pattern, or restructure your code to avoid triggering the pattern.

#### `.env` Pattern

Secrets flow through environment variables, never through code:

1. `.env.example` — Committed. Documents all available environment variables with safe
   defaults. Contains no real secrets.
2. `.env` — Gitignored. Contains actual secrets for local development. Never committed.
3. CI/production — Secrets injected via platform environment variables (GitHub Secrets,
   Docker env, cloud provider secret stores).

#### `.gitignore` Coverage

The `.gitignore` file blocks common secret file types from being committed:

- `.env`, `.env.local`, `.env.*.local` — Environment files
- `*.pem`, `*.key`, `*.p12`, `*.pfx` — Private keys and certificates
- `credentials/`, `secrets/` — Secret directories
- `*.credential`, `*.keystore` — Credential files

### Docker & Container Security

#### Non-Root User

The container runs as `appuser` (not `root`). If the application is compromised, the
attacker:

- Cannot install system packages
- Cannot modify system files
- Cannot access other containers' data
- Has limited file system access

#### Multi-Stage Build

Development tools (uv, compilers, build dependencies) exist only in the builder stage. The
runtime image contains only the Python interpreter, the virtual environment, and your source
code. This reduces the attack surface by removing tools an attacker could use.

#### `.dockerignore`

Excludes sensitive and unnecessary files from the Docker build context: tests, docs,
scripts, `.git`, `.github`, `.claude`, caches, `.env` files. This prevents secrets from
being accidentally baked into Docker layers.

#### HEALTHCHECK

The `HEALTHCHECK` instruction tells container orchestrators (Docker Swarm, Kubernetes via
liveness probes) how to verify the container is running correctly. Unhealthy containers are
automatically restarted, improving availability.

### CI/CD Security

#### Least-Privilege Permissions

The GitHub Actions workflow uses `permissions: contents: read` — it can read your code but
cannot push, create releases, or modify repository settings. This limits the blast radius
if a CI step is compromised.

#### Pinned Action Versions

All GitHub Actions are pinned to specific major versions (e.g., `@v6`, `@v7`) rather than
`@latest`. This prevents supply chain attacks where a compromised action version is deployed.

#### Three-Tier Pipeline

The CI pipeline runs three independent job types:

1. **`quality`** — Lint, format check, type check (fast, catches most issues)
2. **`test`** — Full test suite with coverage (runs only if quality passes)
3. **`security`** — Semgrep SAST + pip-audit CVE scan (runs independently)

The security job runs in parallel with quality/test, ensuring security checks are never
skipped even if tests fail.

### SECURITY.md

The `SECURITY.md` file documents how to report vulnerabilities, response timelines, and
supported versions. See the file for details.

### Security Commands Reference

| Command | Purpose |
|---------|---------|
| `make audit` | Scan dependencies for known vulnerabilities (CVEs) |
| `make check` | Runs lint (including S and B security rules), format, typecheck, and tests |
| `make lint` | Includes ruff S (bandit) and B (bugbear) security checks |
| `uv run pre-commit run gitleaks --all-files` | Scan all files for committed secrets |

---

## Design Decisions & Trade-offs

### Why uv over pip/poetry

- **10-100x faster** than pip for dependency resolution
- **Lockfile support** (`uv.lock`) for reproducible builds — pip requires a separate tool
  (pip-tools) for this
- **Python version management** built in — replaces pyenv
- **Single binary** replaces pip + venv + pip-tools + pyenv

### Why src Layout over Flat

- **Prevents accidental imports**: Without `src/`, Python can import your package from the
  project root directory even if it is not installed. This masks packaging bugs.
- **PyPA recommended**: The Python Packaging Authority recommends src layout for packages
  intended to be installed.
- **Cleaner separation**: Source, tests, docs, and config each have their own top-level
  directory.

### Why Ruff over Black + Flake8 + isort

- **Single tool** replaces 5+ legacy tools (Black, Flake8, isort, pydocstyle, pyupgrade,
  autoflake)
- **100x faster** than Flake8 (Rust implementation)
- **Identical output** to Black for formatting
- **Less configuration** — one `[tool.ruff]` section instead of three

### Why hatchling over setuptools

- **Standards-compliant**: Implements PEP 517/518/621 without legacy baggage
- **Minimal config**: No `setup.py` or `setup.cfg` needed
- **uv default**: The backend `uv init` chooses by default
- **Handles src layout**: Automatically discovers packages in `src/`

### Why stdlib dataclasses over pydantic

- **Zero runtime dependencies**: The scaffold starts with an empty `dependencies = []`. You
  can add pydantic later with one line.
- **Familiar pattern**: `dataclasses` is stdlib, no learning curve
- **Easy upgrade path**: Changing `@dataclass` to `class Settings(BaseSettings)` is a
  minimal refactor

### Why 100% Coverage Threshold

- **Complete confidence**: Every line and branch is tested — no untested code paths
- **Prevents coverage erosion**: New code must include tests, no exceptions
- **Achievable with exclusions**: `if __name__` guards and `TYPE_CHECKING` blocks are
  excluded since they cannot meaningfully be tested
- **Adjustable**: Change `fail_under` in `pyproject.toml` to relax if needed

### Why `uv.lock` is Committed

- **Reproducible builds**: Everyone on the team installs exactly the same dependency
  versions
- **CI consistency**: The CI pipeline uses `--frozen` to install from the lockfile without
  re-resolving
- **Recommended by uv**: The official uv documentation recommends committing `uv.lock`
