import httpx


GITHUB_API_URL = "https://api.github.com"


def fetch_repository_metrics(repository: str) -> dict:
    """
    Fetch the current star and fork counts for a GitHub repository.

    repository format:
        owner/repository
    """

    url = f"{GITHUB_API_URL}/repos/{repository}"

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "frontier-intelligence-pipeline",
    }

    response = httpx.get(
        url,
        headers=headers,
        timeout=20.0,
    )

    response.raise_for_status()

    data = response.json()

    return {
        "repository": repository,
        "stars": data.get("stargazers_count", 0),
        "forks": data.get("forks_count", 0),
    }
from app.database.db import get_connection


def save_repository_metrics(metrics: dict) -> None:
    """
    Save a point-in-time GitHub metrics snapshot.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO repository_metrics (
                repository,
                stars,
                forks
            )
            VALUES (?, ?, ?)
            """,
            (
                metrics["repository"],
                metrics["stars"],
                metrics["forks"],
            ),
        )

        connection.commit()

    finally:
        connection.close()