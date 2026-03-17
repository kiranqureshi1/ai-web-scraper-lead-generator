from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    openai_model: str
    database_url: str
    http_timeout: int
    http_max_retries: int
    openai_max_retries: int
    retry_base_delay: float
    user_agent: str
    content_char_limit: int

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()

        return cls(
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            database_url=os.getenv(
                "DATABASE_URL",
                "postgresql+psycopg2://postgres:postgres@localhost:5432/leadgen",
            ),
            http_timeout=int(os.getenv("HTTP_TIMEOUT", "20")),
            http_max_retries=int(os.getenv("HTTP_MAX_RETRIES", "3")),
            openai_max_retries=int(os.getenv("OPENAI_MAX_RETRIES", "3")),
            retry_base_delay=float(os.getenv("RETRY_BASE_DELAY", "1.0")),
            user_agent=os.getenv(
                "USER_AGENT",
                "LeadGenBot/1.0 (+https://github.com/your-username/ai-web-scraper-lead-generator)",
            ),
            content_char_limit=int(os.getenv("CONTENT_CHAR_LIMIT", "6000")),
        )
