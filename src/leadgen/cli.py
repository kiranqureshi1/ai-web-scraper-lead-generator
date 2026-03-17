from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import Settings
from .pipeline import LeadPipeline


def load_urls(file_path: str) -> list[str]:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    urls: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        urls.append(stripped)
    return urls


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI Web Scraper + Lead Generator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Scrape and extract leads for many websites")
    run_parser.add_argument("--input", required=True, help="Path to a txt file with one URL per line")

    single_parser = subparsers.add_parser("scrape", help="Scrape and extract a single website")
    single_parser.add_argument("--url", required=True, help="Website URL")

    export_parser = subparsers.add_parser("export", help="Export all leads from database to CSV")
    export_parser.add_argument("--output", default="exports/leads.csv", help="CSV output path")

    return parser


def run_command(args: argparse.Namespace) -> int:
    settings = Settings.from_env()
    pipeline = LeadPipeline(settings)
    pipeline.init_db()

    if args.command == "run":
        urls = load_urls(args.input)
        success_count = 0
        failed: list[tuple[str, str]] = []

        for url in urls:
            try:
                lead = pipeline.run_single(url)
                success_count += 1
                print(f"Saved lead: {lead.company} | {lead.email} | {lead.website}")
            except Exception as exc:  # noqa: BLE001
                failed.append((url, str(exc)))
                print(f"Failed: {url} | {exc}")

        print(f"Processed {len(urls)} websites. Success: {success_count}. Failed: {len(failed)}.")
        return 0

    if args.command == "scrape":
        lead = pipeline.run_single(args.url)
        print("Lead saved:")
        print(f"Company:  {lead.company}")
        print(f"Email:    {lead.email}")
        print(f"Industry: {lead.industry}")
        print(f"Location: {lead.location}")
        print(f"Website:  {lead.website}")
        return 0

    if args.command == "export":
        output_path = pipeline.export_csv(args.output)
        print(f"CSV exported: {output_path}")
        return 0

    raise ValueError(f"Unknown command: {args.command}")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        exit_code = run_command(args)
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
