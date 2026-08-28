from types import SimpleNamespace

from app.extraction.extractor import extract_organization


def test_malformed_ai_output_returns_unknown(monkeypatch):
    mock_response = SimpleNamespace(
        output_parsed=None
    )

    def mock_parse(*args, **kwargs):
        return mock_response

    monkeypatch.setattr(
        "app.extraction.extractor.client.responses.parse",
        mock_parse,
    )

    result = extract_organization(
        "This text does not contain reliable organization data."
    )

    assert result.name == "Unknown"
    assert result.description is None
    assert result.website is None
    assert result.founded_year is None
    assert result.category is None