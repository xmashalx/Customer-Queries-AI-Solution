"""This module calls the OpenAI API to analyze customer support queries."""

from openai import OpenAI
import os
from dotenv import load_dotenv


def load_system_prompt() -> str:
    with open("system_prompt.txt", "r") as f:
        return f.read()


def analyse_query(query: str, client: OpenAI = None) -> str:
    """Call the OpenAI API and return raw JSON string."""

    system_prompt = load_system_prompt()

    response = client.chat.completions.create(
        model="gpt-5-nano",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f'Customer Enquiry:\n"{query}"\n\nReturn JSON only.'}
        ]
    )

    return response.choices[0].message.content
