import asyncio
import random

import httpx


MAX_RETRIES = 5


async def fetch_page(url: str):
    async with httpx.AsyncClient(
        timeout=20,
        follow_redirects=True,
        headers={
            "User-Agent": "FrontierIntelligencePipeline/1.0"
        },
    ) as client:

        for attempt in range(MAX_RETRIES):
            try:
                response = await client.get(url)

                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")

                    if retry_after:
                        wait_time = float(retry_after)
                    else:
                        wait_time = min(2 ** attempt, 30) + random.random()

                    print(
                        f"429 rate limit. "
                        f"Retrying in {wait_time:.2f}s..."
                    )

                    await asyncio.sleep(wait_time)
                    continue

                response.raise_for_status()

                return response

            except httpx.HTTPError as error:
                if attempt == MAX_RETRIES - 1:
                    raise

                wait_time = min(2 ** attempt, 30) + random.random()

                print(
                    f"Request failed: {error}. "
                    f"Retrying in {wait_time:.2f}s..."
                )

                await asyncio.sleep(wait_time)

        raise RuntimeError("Maximum retries exceeded")