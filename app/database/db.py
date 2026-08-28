import sqlite3
from pathlib import Path


DATABASE_PATH = Path("data/intelligence.db")


def get_connection():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)

    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS organizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            website TEXT,
            founded_year INTEGER,
            category TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL UNIQUE,
            title TEXT,
            raw_text TEXT,
            source_published_at TEXT,
            discovered_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            scraped_at TEXT,
            processed_at TEXT
        );

        CREATE TABLE IF NOT EXISTS repository_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repository TEXT NOT NULL,
            stars INTEGER,
            forks INTEGER,
            observed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    connection.commit()
    connection.close()


if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully!")