from __future__ import annotations

import re
import time
from dataclasses import dataclass
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}")
RETRYABLE_HTTP_STATUS = {408, 425, 429, 500, 502, 503, 504}


@dataclass
class ScrapedPage:
    website: str
    title: str
    text_content: str
    email_candidates: list[str]


class WebsiteScraper:
    def __init__(self, timeout: int, user_agent: str, max_retries: int, base_delay: float) -> None:
        self.timeout = timeout
        self.headers = {"User-Agent": user_agent}
        self.max_retries = max(0, max_retries)
        self.base_delay = max(0.1, base_delay)

    @staticmethod
    def normalize_url(url: str) -> str:
        trimmed = url.strip()
        if not trimmed:
            raise ValueError("URL cannot be empty")

        parsed = urlparse(trimmed)
        if parsed.scheme:
            return trimmed
        return f"https://{trimmed}"

    def fetch(self, url: str) -> str:
        normalized_url = self.normalize_url(url)
        attempts = self.max_retries + 1

        for attempt in range(attempts):
            try:
                response = requests.get(normalized_url, headers=self.headers, timeout=self.timeout)
                response.raise_for_status()
                return response.text
            except requests.RequestException as exc:
                if attempt == attempts - 1 or not self._is_retryable(exc):
                    raise

                delay = self.base_delay * (2**attempt)
                time.sleep(delay)

        raise RuntimeError("HTTP fetch failed after retries")

    @staticmethod
    def _is_retryable(error: requests.RequestException) -> bool:
        response = getattr(error, "response", None)
        if response is None:
            return True

        status_code = getattr(response, "status_code", None)
        return status_code in RETRYABLE_HTTP_STATUS

    def parse(self, website: str, html: str) -> ScrapedPage:
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        title = (soup.title.string or "").strip() if soup.title else ""
        text_content = " ".join(soup.stripped_strings)

        email_candidates = sorted(set(EMAIL_PATTERN.findall(html + " " + text_content)))

        return ScrapedPage(
            website=website,
            title=title,
            text_content=text_content,
            email_candidates=email_candidates,
        )
