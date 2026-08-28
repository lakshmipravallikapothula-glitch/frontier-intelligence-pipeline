import os

import pytest

from app.extraction.extractor import extract_organization


text = """
OpenAI is an artificial intelligence research and deployment company.
The company was founded in 2015 and develops advanced AI systems.
Its official website is https://openai.com.
"""


@pytest.mark.skipif(
    not os.getenv("RUN_LLM_TEST"),
    reason="Live LLM test disabled. Set RUN_LLM_TEST=1 to run it.",
)
def test_llm_extraction():
    result = extract_organization(text)

    assert result is not None
    assert result.name
    assert result.name != "Unknown"