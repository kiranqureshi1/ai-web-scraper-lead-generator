from __future__ import annotations

import json
import time
from dataclasses import dataclass
from json import JSONDecodeError

from openai import APIConnectionError, APIStatusError, OpenAI, RateLimitError

from .scraper import ScrapedPage


@dataclass
class ExtractedLead:
    company: str
    email: str
    industry: str
    location: str


class AILeadExtractor:
    def __init__(
        self,
        api_key: str,
        model: str,
        content_char_limit: int,
        max_retries: int,
        base_delay: float,
    ) -> None:
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set")

        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.content_char_limit = content_char_limit
        self.max_retries = max(0, max_retries)
        self.base_delay = max(0.1, base_delay)

    def extract(self, page: ScrapedPage) -> ExtractedLead:
        prompt = self._build_prompt(page)

        completion = self._create_completion(prompt)

        content = completion.choices[0].message.content or "{}"
        payload = self._parse_json_payload(content)

        return ExtractedLead(
            company=self._clean(payload.get("company")),
            email=self._clean(payload.get("email")),
            industry=self._clean(payload.get("industry")),
            location=self._clean(payload.get("location")),
        )

    def _build_prompt(self, page: ScrapedPage) -> str:
        content = page.text_content[: self.content_char_limit]
        emails = ", ".join(page.email_candidates) if page.email_candidates else "none"

        return (
            f"Website: {page.website}\n"
            f"Page title: {page.title or 'Unknown'}\n"
            f"Detected emails: {emails}\n"
            "Content:\n"
            f"{content}"
        )

    @staticmethod
    def _clean(value: object) -> str:
        if not value:
            return "Unknown"

        cleaned = str(value).strip()
        return cleaned if cleaned else "Unknown"

    @staticmethod
    def _parse_json_payload(content: str) -> dict[str, object]:
        try:
            parsed = json.loads(content)
            return parsed if isinstance(parsed, dict) else {}
        except JSONDecodeError:
            # Some models may wrap JSON in markdown fences.
            cleaned = content.strip().replace("```json", "").replace("```", "").strip()
            try:
                parsed = json.loads(cleaned)
                return parsed if isinstance(parsed, dict) else {}
            except JSONDecodeError:
                return {}

    def _create_completion(self, prompt: str):
        attempts = self.max_retries + 1

        for attempt in range(attempts):
            try:
                return self.client.chat.completions.create(
                    model=self.model,
                    temperature=0,
                    response_format={"type": "json_object"},
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "Extract lead information from website content. "
                                "Return valid JSON only with keys: company, email, industry, location. "
                                "If a field is missing, return \"Unknown\"."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                )
            except (RateLimitError, APIConnectionError, APIStatusError) as exc:
                if attempt == attempts - 1 or not self._is_retryable(exc):
                    raise

                delay = self.base_delay * (2**attempt)
                time.sleep(delay)

        raise RuntimeError("OpenAI completion failed after retries")

    @staticmethod
    def _is_retryable(error: Exception) -> bool:
        if isinstance(error, (RateLimitError, APIConnectionError)):
            return True

        if isinstance(error, APIStatusError):
            return error.status_code in {408, 425, 429, 500, 502, 503, 504}

        return False
