# Copilot Instructions (Project Overrides)

This repository inherits shared defaults from `../../.github/copilot-instructions.md`.
Use this file only for project-specific rules that should override or extend the shared defaults.

## Project Context

- Python CLI project for scraping websites, extracting structured leads with OpenAI, storing in PostgreSQL, and exporting CSV.
- Python version target: 3.10+.
- Main package path: `src/leadgen`.
- CLI entrypoint: `leadgen.cli:main`.

## Project-Specific Development Rules

- Keep existing CLI commands and flags stable unless explicitly requested to change.
- Preserve fallback behavior where unknown extracted fields are stored as `Unknown` unless instructed otherwise.
- Preserve retry/backoff behavior for transient HTTP/OpenAI failures unless requested.
- Keep DB schema compatibility unless the task explicitly includes migration work.

## Project Run Commands

- Batch: `leadgen run --input data/websites.txt`
- Single site: `leadgen scrape --url <url>`
- Export CSV: `leadgen export --output exports/leads.csv`
