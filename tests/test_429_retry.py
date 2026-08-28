import httpx
import pytest

from app.crawler.fetcher import fetch_page


@pytest.mark.anyio
async def test_fetch_page_retries_after_429(monkeypatch):
    responses = [
        httpx.Response(
            429,
            headers={"Retry-After": "0"},
            request=httpx.Request(
                "GET",
                "https://example.com",
            ),
        ),
        httpx.Response(
            200,
            text="<html><body>Hello</body></html>",
            request=httpx.Request(
                "GET",
                "https://example.com",
            ),
        ),
    ]

    calls = []

    async def mock_get(self, url):
        calls.append(url)
        return responses.pop(0)

    async def mock_sleep(seconds):
        return None

    monkeypatch.setattr(
        "httpx.AsyncClient.get",
        mock_get,
    )

    monkeypatch.setattr(
        "app.crawler.fetcher.asyncio.sleep",
        mock_sleep,
    )

    response = await fetch_page(
        "https://example.com"
    )

    assert response.status_code == 200
    assert len(calls) == 2