from app.extraction.chunker import chunk_text
from app.extraction.pipeline import merge_organizations
from app.extraction.extractor import Organization


def test_large_document_is_chunked():
    text = "OpenAI develops artificial intelligence systems. " * 1000

    chunks = chunk_text(
        text,
        max_chars=12000,
        overlap=1000,
    )

    assert len(chunks) > 1

    for chunk in chunks:
        assert len(chunk) <= 12000


def test_chunk_results_are_merged():
    results = [
        Organization(
            name="OpenAI",
            description=None,
            website="https://openai.com",
            founded_year=None,
            category=None,
        ),
        Organization(
            name="OpenAI",
            description="AI research and deployment company",
            website=None,
            founded_year=2015,
            category="AI",
        ),
    ]

    merged = merge_organizations(results)

    assert merged.name == "OpenAI"
    assert merged.website == "https://openai.com"
    assert merged.founded_year == 2015
    assert merged.category == "AI"
    assert merged.description == "AI research and deployment company"