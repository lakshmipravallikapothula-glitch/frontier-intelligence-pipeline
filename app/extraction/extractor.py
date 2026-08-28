import os
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field


# Load variables from .env
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError(
        "OPENAI_API_KEY is missing. "
        "Add it to the .env file."
    )

client = OpenAI(api_key=api_key)


class Organization(BaseModel):
    name: str = Field(
        description="Organization or company name"
    )

    description: Optional[str] = Field(
        default=None,
        description="Short description of the organization"
    )

    website: Optional[str] = Field(
        default=None,
        description="Official website"
    )

    founded_year: Optional[int] = Field(
        default=None,
        description="Year the organization was founded"
    )

    category: Optional[str] = Field(
        default=None,
        description="Main category, such as AI, SaaS, Robotics, etc."
    )


def extract_organization(text: str) -> Organization:
    """
    Extract organization information from text using an LLM.

    The LLM returns structured data that is validated
    against the Organization Pydantic model.
    """

    if not text or not text.strip():
        return Organization(name="Unknown")

    response = client.responses.parse(
        model="gpt-4o-mini",
        input=[
            {
                "role": "system",
                "content": (
                    "You are an information extraction system. "
                    "Extract organization information from the "
                    "provided text. Only use information supported "
                    "by the text. If a field is unknown, return null."
                ),
            },
            {
                "role": "user",
                "content": text,
            },
        ],
        text_format=Organization,
    )

    result = response.output_parsed

    if result is None:
        return Organization(name="Unknown")

    return result