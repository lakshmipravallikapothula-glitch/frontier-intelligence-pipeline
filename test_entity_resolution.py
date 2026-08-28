from app.entity_resolution.resolver import (
    normalize_name,
    names_match,
)


def test_normalize_name():
    assert normalize_name("OpenAI Inc.") == "openai"
    assert normalize_name("OpenAI, Inc.") == "openai"
    assert normalize_name("OPEN AI") == "open ai"


def test_exact_entity_match():
    assert names_match("OpenAI Inc.", "OpenAI, Inc.")


def test_similar_entity_match():
    assert names_match("OpenAI Corporation", "OpenAI Corp.")


def test_different_entities():
    assert not names_match("OpenAI", "Microsoft")