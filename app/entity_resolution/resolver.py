import re
import unicodedata
from difflib import SequenceMatcher


def normalize_name(name: str) -> str:
    """
    Normalize an organization name for entity matching.

    Examples:
        OpenAI
        OpenAI Inc.
        OpenAI, Inc.
        OPEN AI

    become approximately the same normalized identity.
    """

    if not name:
        return ""

    # Normalize Unicode characters
    value = unicodedata.normalize("NFKD", name)

    # Convert to lowercase
    value = value.lower()

    # Remove punctuation
    value = re.sub(r"[^\w\s]", " ", value)

    # Remove common legal entity suffixes
    suffixes = [
        "incorporated",
        "inc",
        "corporation",
        "corp",
        "company",
        "co",
        "limited",
        "ltd",
        "llc",
        "plc",
    ]

    words = value.split()

    while words and words[-1] in suffixes:
        words.pop()

    # Remove whitespace differences
    value = " ".join(words)

    return value.strip()


def names_match(
    name1: str,
    name2: str,
    threshold: float = 0.90,
) -> bool:
    """
    Determine whether two organization names likely
    refer to the same organization.
    """

    normalized1 = normalize_name(name1)
    normalized2 = normalize_name(name2)

    if not normalized1 or not normalized2:
        return False

    # Exact normalized match
    if normalized1 == normalized2:
        return True

    # Similarity match
    similarity = SequenceMatcher(
        None,
        normalized1,
        normalized2,
    ).ratio()

    return similarity >= threshold