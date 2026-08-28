import asyncio
from datetime import datetime, timezone

from bs4 import BeautifulSoup

from app.crawler.fetcher import fetch_page
from app.extraction.pipeline import extract_with_chunking
from app.database.db import get_connection, initialize_database
from app.entity_resolution.database_resolver import save_or_update_organization
from app.metrics.github_metrics import (
    fetch_repository_metrics,
    save_repository_metrics,
)

GITHUB_REPOSITORY = "openai/openai-python"


async def process_url(url: str):
    print(f"\nProcessing: {url}")

    # 1. Crawl
    response = await fetch_page(url)

    print(f"✓ Downloaded ({response.status_code})")

    # 2. Extract readable text from HTML
    soup = BeautifulSoup(response.text, "html.parser")

    title = (
        soup.title.string.strip()
        if soup.title and soup.title.string
        else "No title"
    )

    raw_text = soup.get_text(" ", strip=True)

    print(f"✓ Extracted {len(raw_text)} characters of text")

    # 3. AI structured extraction with 413 recovery
    organization = extract_with_chunking(raw_text)

    print(f"✓ Organization detected: {organization.name}")

    # 4. Save crawled document
    connection = get_connection()

    try:
        cursor = connection.cursor()

        now = datetime.now(timezone.utc).isoformat()

        cursor.execute(
            """
            INSERT INTO documents (
                url,
                title,
                raw_text,
                discovered_at,
                scraped_at,
                processed_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(url) DO UPDATE SET
                title = excluded.title,
                raw_text = excluded.raw_text,
                scraped_at = excluded.scraped_at,
                processed_at = excluded.processed_at
            """,
            (
                url,
                title,
                raw_text,
                now,
                now,
                now,
            ),
        )

        connection.commit()

    finally:
        connection.close()

    print("✓ Document saved")

    # 5. Resolve and save organization
    if organization.name != "Unknown":
        organization_id = save_or_update_organization(
            organization
        )

        if organization_id == -1:
            print("⚠ Organization could not be resolved")
        else:
            print(
                f"✓ Organization resolved "
                f"(ID: {organization_id})"
            )
    else:
        print("⚠ No organization detected")

    # 6. Fetch and save GitHub repository metrics
    print(
        f"Fetching GitHub metrics for "
        f"{GITHUB_REPOSITORY}..."
    )

    try:
        metrics = fetch_repository_metrics(
            GITHUB_REPOSITORY
        )

        save_repository_metrics(metrics)

        print(
            f"✓ GitHub metrics saved: "
            f"{metrics['stars']} stars, "
            f"{metrics['forks']} forks"
        )

    except Exception as exc:
        print(
            f"⚠ GitHub metrics collection failed: "
            f"{exc}"
        )

    print("✓ Processing complete")


async def main():
    print("🚀 Starting AI data-ingestion pipeline")

    initialize_database()

    url = "https://openai.com"

    await process_url(url)

    print("\nPipeline completed successfully! 🚀")


if __name__ == "__main__":
    asyncio.run(main())