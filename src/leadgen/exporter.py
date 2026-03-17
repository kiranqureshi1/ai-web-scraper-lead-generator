from __future__ import annotations

import csv
from pathlib import Path

from .models import Lead


def export_leads_to_csv(leads: list[Lead], output_path: str) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Company", "Email", "Industry", "Location", "Website"])

        for lead in leads:
            writer.writerow([
                lead.company,
                lead.email,
                lead.industry,
                lead.location,
                lead.website,
            ])

    return path
