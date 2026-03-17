# AI Web Scraper + Lead Generator

Scrapes company websites, extracts structured lead data with OpenAI, stores records in PostgreSQL, and exports leads to CSV.

## Features

- Web scraping with `requests` + `BeautifulSoup`
- AI lead extraction via OpenAI API
- PostgreSQL storage with SQLAlchemy
- CSV export pipeline
- CLI workflow for single site or batch runs

## Stack

- Python
- BeautifulSoup
- OpenAI API
- PostgreSQL

## Example Output

| Company | Email | Industry | Location | Website |
| --- | --- | --- | --- | --- |
| Acme Labs | hello@acmelabs.com | SaaS | Berlin, Germany | https://acmelabs.com |

## Project Structure

```text
ai-web-scraper-lead-generator/
  src/leadgen/
    cli.py
    config.py
    database.py
    exporter.py
    extractor.py
    models.py
    pipeline.py
    repository.py
    scraper.py
  data/websites.txt
  docker-compose.yml
  pyproject.toml
  requirements.txt
```

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
pip install -e .
```

3. Start PostgreSQL:

```bash
docker compose up -d
```

4. Copy `.env.example` to `.env` and set your OpenAI key.

## Usage

### Batch run

```bash
leadgen run --input data/websites.txt
```

### Single website

```bash
leadgen scrape --url https://example.com
```

### Export CSV

```bash
leadgen export --output exports/leads.csv
```

## Data Model

`Lead` table fields:

- `company`
- `email`
- `industry`
- `location`
- `website`
- `scraped_at`

## Notes

- If AI cannot infer a field, it is stored as `Unknown`.
- If AI does not return an email and scraper finds one, the first discovered email is used.
- Transient HTTP/OpenAI failures are retried with exponential backoff.
