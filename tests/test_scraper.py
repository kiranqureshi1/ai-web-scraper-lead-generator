from leadgen.scraper import WebsiteScraper


def test_normalize_url_adds_scheme() -> None:
    assert WebsiteScraper.normalize_url("example.com") == "https://example.com"


def test_parse_extracts_email() -> None:
  scraper = WebsiteScraper(timeout=10, user_agent="test-agent", max_retries=1, base_delay=0.1)
    html = """
    <html>
      <head><title>Example Corp</title></head>
      <body>
        <p>Contact us at contact@example.com</p>
      </body>
    </html>
    """

    page = scraper.parse("https://example.com", html)

    assert page.title == "Example Corp"
    assert "contact@example.com" in page.email_candidates
