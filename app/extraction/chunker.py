from typing import List


def chunk_text(
    text: str,
    max_chars: int = 12000,
    overlap: int = 1000,
) -> List[str]:
    """
    Split large text into overlapping chunks.

    Args:
        text: Input document text.
        max_chars: Maximum characters per chunk.
        overlap: Number of characters shared between chunks.

    Returns:
        List of text chunks.
    """

    if not text:
        return []

    if max_chars <= 0:
        raise ValueError("max_chars must be greater than 0")

    if overlap < 0:
        raise ValueError("overlap cannot be negative")

    if overlap >= max_chars:
        raise ValueError("overlap must be smaller than max_chars")

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + max_chars, len(text))

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = end - overlap

    return chunks