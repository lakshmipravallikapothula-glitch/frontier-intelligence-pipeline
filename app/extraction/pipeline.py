from typing import List

from openai import BadRequestError

from app.extraction.chunker import chunk_text
from app.extraction.extractor import Organization, extract_organization


def merge_organizations(
    organizations: List[Organization],
) -> Organization:
    """
    Merge organization information extracted from multiple chunks.

    The first non-empty value for each field is kept.
    """

    if not organizations:
        return Organization(name="Unknown")

    name = "Unknown"
    description = None
    website = None
    founded_year = None
    category = None

    for organization in organizations:
        if name == "Unknown" and organization.name != "Unknown":
            name = organization.name

        if description is None and organization.description:
            description = organization.description

        if website is None and organization.website:
            website = organization.website

        if founded_year is None and organization.founded_year:
            founded_year = organization.founded_year

        if category is None and organization.category:
            category = organization.category

    return Organization(
        name=name,
        description=description,
        website=website,
        founded_year=founded_year,
        category=category,
    )


def extract_with_chunking(
    text: str,
    max_chars: int = 12000,
) -> Organization:
    """
    Extract organization information from a document.

    First attempts normal extraction.

    If the LLM rejects the document because it is too large,
    the document is split into chunks and each chunk is extracted
    separately.
    """

    try:
        return extract_organization(text)

    except BadRequestError as error:
        error_text = str(error).lower()

        if "413" not in error_text and "too large" not in error_text:
            raise

        chunks = chunk_text(
            text,
            max_chars=max_chars,
            overlap=1000,
        )

        extracted = []

        for chunk in chunks:
            result = extract_organization(chunk)

            if result.name != "Unknown":
                extracted.append(result)

        return merge_organizations(extracted)