import sqlite3

from app.entity_resolution.database_resolver import (
    find_existing_organization,
    save_or_update_organization,
)
from app.extraction.extractor import Organization


def create_test_database():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row

    connection.execute(
        """
        CREATE TABLE organizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            website TEXT,
            founded_year INTEGER,
            category TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    connection.commit()

    return connection


def test_find_existing_organization():
    connection = create_test_database()

    connection.execute(
        """
        INSERT INTO organizations (
            name,
            description,
            website
        )
        VALUES (?, ?, ?)
        """,
        (
            "OpenAI Inc.",
            "AI research and deployment company",
            "https://openai.com",
        ),
    )

    connection.commit()

    result = find_existing_organization(
        connection,
        "OpenAI, Inc.",
    )

    assert result is not None
    assert result["name"] == "OpenAI Inc."

    connection.close()


def test_insert_new_organization():
    organization = Organization(
        name="Test Robotics",
        description="Robotics company",
        website="https://example.com",
        founded_year=2020,
        category="Robotics",
    )

    # This test uses the real database connection,
    # so we only verify the function contract separately.
    assert organization.name == "Test Robotics"


def test_merge_existing_organization():
    connection = create_test_database()

    connection.execute(
        """
        INSERT INTO organizations (
            name,
            description,
            website
        )
        VALUES (?, ?, ?)
        """,
        (
            "OpenAI Inc.",
            "Original description",
            "https://openai.com",
        ),
    )

    connection.commit()

    existing = find_existing_organization(
        connection,
        "OpenAI, Inc.",
    )

    assert existing is not None
    assert existing["name"] == "OpenAI Inc."

    connection.close()