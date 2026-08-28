from app.database.db import get_connection, initialize_database


def test_duplicate_url_updates_existing_document():
    initialize_database()

    url = "https://example.com/duplicate-test"

    connection = get_connection()

    try:
        cursor = connection.cursor()

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
                "First Title",
                "First content",
                "2026-08-28T10:00:00+00:00",
                "2026-08-28T10:00:00+00:00",
                "2026-08-28T10:00:00+00:00",
            ),
        )

        connection.commit()

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
                "Updated Title",
                "Updated content",
                "2026-08-28T10:00:00+00:00",
                "2026-08-28T11:00:00+00:00",
                "2026-08-28T11:00:00+00:00",
            ),
        )

        connection.commit()

        row = cursor.execute(
            """
            SELECT title, raw_text
            FROM documents
            WHERE url = ?
            """,
            (url,),
        ).fetchone()

        count = cursor.execute(
            """
            SELECT COUNT(*)
            FROM documents
            WHERE url = ?
            """,
            (url,),
        ).fetchone()[0]

    finally:
        connection.close()

    assert count == 1
    assert row[0] == "Updated Title"
    assert row[1] == "Updated content"