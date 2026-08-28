import httpx

from app.metrics.github_metrics import (
    fetch_repository_metrics,
    save_repository_metrics,
)
from app.database.db import get_connection


def test_fetch_repository_metrics(monkeypatch):
    def mock_get(*args, **kwargs):
        return httpx.Response(
            200,
            json={
                "full_name": "openai/example",
                "stargazers_count": 125,
                "forks_count": 30,
            },
            request=httpx.Request(
                "GET",
                "https://api.github.com/repos/openai/example",
            ),
        )

    monkeypatch.setattr(
        "app.metrics.github_metrics.httpx.get",
        mock_get,
    )

    result = fetch_repository_metrics(
        "openai/example"
    )

    assert result["repository"] == "openai/example"
    assert result["stars"] == 125
    assert result["forks"] == 30


def test_save_repository_metrics():
    metrics = {
        "repository": "openai/example",
        "stars": 125,
        "forks": 30,
    }

    save_repository_metrics(metrics)

    conn = get_connection()

    row = conn.execute(
        """
        SELECT repository, stars, forks
        FROM repository_metrics
        ORDER BY id DESC
        LIMIT 1
        """
    ).fetchone()

    conn.close()

    assert row is not None
    assert row[0] == "openai/example"
    assert row[1] == 125
    assert row[2] == 30


def test_historical_metrics_are_preserved():
    first = {
        "repository": "openai/example",
        "stars": 100,
        "forks": 20,
    }

    second = {
        "repository": "openai/example",
        "stars": 150,
        "forks": 30,
    }

    save_repository_metrics(first)
    save_repository_metrics(second)

    conn = get_connection()

    rows = conn.execute(
        """
        SELECT stars, forks
        FROM repository_metrics
        WHERE repository = ?
        ORDER BY id DESC
        LIMIT 2
        """,
        ("openai/example",),
    ).fetchall()

    conn.close()

    assert len(rows) == 2
    assert rows[0][0] == 150
    assert rows[0][1] == 30
    assert rows[1][0] == 100
    assert rows[1][1] == 20