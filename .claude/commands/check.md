Run the full quality gate sequence and report results for each step:

1. `uv run ruff check .`
2. `uv run ruff format --check .`
3. `uv run mypy src/`
4. `uv run pytest`

If any step fails, stop and report the failure with details.
Report a summary at the end showing PASS or FAIL for each gate.
