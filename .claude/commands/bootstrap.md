Help the user initialize this scaffold as a new project.

Ask the user for their desired project name. Validate that it:
- Is a valid Python identifier (snake_case)
- Does not contain hyphens (suggest underscores instead)
- Is not "myproject" (the placeholder name)

Then run:
`python scripts/bootstrap.py <project_name>`

After the script completes, instruct the user to run:
1. `rm -rf .git && git init`
2. `uv sync --extra dev`
3. `uv run pre-commit install`
4. `make check`
5. `git add . && git commit -m "Initial commit"`
