from typing import Optional

from app.database.db import get_connection
from app.entity_resolution.resolver import normalize_name, names_match
from app.extraction.extractor import Organization


def find_existing_organization(
    connection,
    organization_name: str,
) -> Optional[dict]:
    """
    Find an existing organization that matches the supplied name.

    Matching happens in two stages:
    1. Exact normalized-name comparison.
    2. Conservative fuzzy-name comparison.
    """

    if not organization_name:
        return None

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            name,
            description,
            website,
            founded_year,
            category
        FROM organizations
        """
    )

    organizations = cursor.fetchall()

    normalized_input = normalize_name(organization_name)

    # First: exact normalized match
    for organization in organizations:
        if normalize_name(organization["name"]) == normalized_input:
            return dict(organization)

    # Second: conservative fuzzy match
    for organization in organizations:
        if names_match(
            organization_name,
            organization["name"],
            threshold=0.90,
        ):
            return dict(organization)

    return None


def save_or_update_organization(
    organization: Organization,
) -> int:
    """
    Insert a new organization or update an existing
    organization when an entity match is found.

    Returns the database ID of the resolved organization.
    """

    if not organization.name or organization.name == "Unknown":
        return -1

    connection = get_connection()

    try:
        existing = find_existing_organization(
            connection,
            organization.name,
        )

        cursor = connection.cursor()

        if existing:
            organization_id = existing["id"]

            # Preserve existing values when the new extraction
            # does not provide them.
            description = (
                organization.description
                if organization.description
                else existing["description"]
            )

            website = (
                organization.website
                if organization.website
                else existing["website"]
            )

            founded_year = (
                organization.founded_year
                if organization.founded_year
                else existing["founded_year"]
            )

            category = (
                organization.category
                if organization.category
                else existing["category"]
            )

            cursor.execute(
                """
                UPDATE organizations
                SET
                    description = ?,
                    website = ?,
                    founded_year = ?,
                    category = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    description,
                    website,
                    founded_year,
                    category,
                    organization_id,
                ),
            )

        else:
            cursor.execute(
                """
                INSERT INTO organizations (
                    name,
                    description,
                    website,
                    founded_year,
                    category
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    organization.name,
                    organization.description,
                    organization.website,
                    organization.founded_year,
                    organization.category,
                ),
            )

            organization_id = cursor.lastrowid

        connection.commit()

        return organization_id

    finally:
        connection.close()