# Copilot Instructions

These instructions apply to all files in this repository.

## Project Context

- This is a Python CLI project for scraping websites, extracting lead data with OpenAI, storing data in PostgreSQL, and exporting CSV.
- Python version target: 3.10+.
- Main package path: `src/leadgen`.
- Primary entrypoint: `leadgen.cli:main`.

## Coding Rules

- Prefer small, focused changes over broad refactors.
- Keep existing public behavior and CLI flags stable unless explicitly asked to change them.
- Follow existing code style and naming patterns in `src/leadgen`.
- Add concise comments only when logic is non-obvious.
- Avoid adding new dependencies unless necessary.

## Testing and Validation

- When changing runtime code, run relevant tests in `tests/`.
- If tests are missing for changed behavior, add or extend tests.
- If a command cannot be run in the current environment, clearly explain what was not validated.

## Data and Reliability

- Preserve current fallback behavior for unknown extracted fields (`Unknown`) unless instructed otherwise.
- Keep retry/backoff behavior for transient HTTP/OpenAI failures unless changes are requested.
- Keep DB schema compatibility unless a migration is explicitly part of the task.

## Preferred Workflow

- For setup and local runs, use commands documented in `README.md`.
- Use batch flow: `leadgen run --input data/websites.txt`.
- Use single-site flow: `leadgen scrape --url <url>`.
- Use export flow: `leadgen export --output exports/leads.csv`.

## Git Update Automation

- After each completed task that changes files, stage relevant files, create a commit, and push to the current branch by default.
- Write commit messages clearly and consistently (prefer Conventional Commit style, e.g., `feat: ...`, `fix: ...`, `docs: ...`, `test: ...`, `chore: ...`).
- Do not force push and do not rewrite history unless explicitly requested.
- If commit or push fails (auth, network, branch protection, conflicts), report the exact blocker and next required user action.
- If no files changed, do not create an empty commit unless explicitly asked.

## User Persistent Preferences

Add your standing preferences below and Copilot should follow them in this repo.

- Auto-commit and push changes to GitHub after each completed task.
- Generate commit messages automatically.
