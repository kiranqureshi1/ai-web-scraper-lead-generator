from __future__ import annotations

from sqlalchemy.orm import Session

from .config import Settings
from .database import create_db_engine, create_session_factory
from .exporter import export_leads_to_csv
from .extractor import AILeadExtractor, ExtractedLead
from .models import Base, Lead
from .repository import LeadRepository
from .scraper import WebsiteScraper


class LeadPipeline:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.engine = create_db_engine(settings.database_url)
        self.session_factory = create_session_factory(self.engine)
        self.scraper = WebsiteScraper(
            timeout=settings.http_timeout,
            user_agent=settings.user_agent,
            max_retries=settings.http_max_retries,
            base_delay=settings.retry_base_delay,
        )
        self.extractor = AILeadExtractor(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            content_char_limit=settings.content_char_limit,
            max_retries=settings.openai_max_retries,
            base_delay=settings.retry_base_delay,
        )
        self.repository = LeadRepository()

    def init_db(self) -> None:
        Base.metadata.create_all(bind=self.engine)

    def run_single(self, raw_url: str) -> Lead:
        website = self.scraper.normalize_url(raw_url)
        html = self.scraper.fetch(website)
        page = self.scraper.parse(website=website, html=html)
        extracted = self.extractor.extract(page)

        extracted = self._fill_email_from_candidates(extracted, page.email_candidates)

        with self.session_factory() as session:
            lead = self.repository.upsert(session, website=website, lead_data=extracted)
            session.commit()
            session.refresh(lead)
            return lead

    def run_many(self, urls: list[str]) -> list[Lead]:
        results: list[Lead] = []
        for raw_url in urls:
            lead = self.run_single(raw_url)
            results.append(lead)
        return results

    def export_csv(self, output_path: str) -> str:
        with self.session_factory() as session:
            leads = self.repository.list_all(session)
        path = export_leads_to_csv(leads=leads, output_path=output_path)
        return str(path)

    @staticmethod
    def _fill_email_from_candidates(extracted: ExtractedLead, candidates: list[str]) -> ExtractedLead:
        if extracted.email != "Unknown":
            return extracted

        if not candidates:
            return extracted

        return ExtractedLead(
            company=extracted.company,
            email=candidates[0],
            industry=extracted.industry,
            location=extracted.location,
        )
