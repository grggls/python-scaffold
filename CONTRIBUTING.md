# Contributing

## Setup

```bash
git clone https://github.com/grggls/myproject.git
cd myproject
make dev          # installs deps + pre-commit hooks
```

## Development workflow

```bash
make format       # auto-format
make check        # lint + format check + typecheck + tests (mirrors CI)
make test-cov     # tests with HTML coverage report
make docs-serve   # live docs preview at localhost:8000
```

All four gates in `make check` must pass before committing. Pre-commit hooks enforce this automatically.

## Submitting changes

1. Create a feature branch: `git checkout -b feat/my-change`
2. Make your changes with tests
3. Run `make check`
4. Open a pull request — fill in the PR template

## Reporting bugs

Use the [bug report template](https://github.com/grggls/myproject/issues/new?template=bug_report.md).

## Security issues

Do **not** open a public issue. Email [gregory.damiani@gmail.com](mailto:gregory.damiani@gmail.com) directly. See [SECURITY.md](SECURITY.md).
