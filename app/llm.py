"""Client configuration; each agent owns its LLM call."""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


def get_llm() -> ChatOpenAI:
    """Create the client only when an agent asks for it, not at import time."""
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    if not os.getenv("OPENAI_API_KEY", "").strip():
        raise ValueError("Configure OPENAI_API_KEY in .env before running the app.")

    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        timeout=60,
        max_retries=0,
    )
