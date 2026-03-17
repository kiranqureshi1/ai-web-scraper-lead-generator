from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from .extractor import ExtractedLead
from .models import Lead


class LeadRepository:
    def upsert(self, session: Session, website: str, lead_data: ExtractedLead) -> Lead:
        existing = session.scalar(select(Lead).where(Lead.website == website))

        if existing:
            existing.company = lead_data.company
            existing.email = lead_data.email
            existing.industry = lead_data.industry
            existing.location = lead_data.location
            existing.scraped_at = datetime.utcnow()
            session.add(existing)
            return existing

        lead = Lead(
            company=lead_data.company,
            email=lead_data.email,
            industry=lead_data.industry,
            location=lead_data.location,
            website=website,
        )
        session.add(lead)
        return lead

    def list_all(self, session: Session) -> list[Lead]:
        rows = session.scalars(select(Lead).order_by(Lead.id.asc())).all()
        return list(rows)
