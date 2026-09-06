"""Research uses a web search tool to gather evidence for the idea."""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_tavily import TavilySearch

from app.state import StartupState


def get_search_tool() -> TavilySearch:
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
    if not os.getenv("TAVILY_API_KEY", "").strip():
        raise ValueError("Configure TAVILY_API_KEY in .env before running web research.")
    return TavilySearch(max_results=3, topic="general")


def format_results(results: dict) -> str:
    items = results.get("results", [])
    if not items:
        return "No relevant web results found."

    lines = []
    for item in items:
        title = item.get("title", "Untitled")
        url = item.get("url", "")
        content = item.get("content", "")
        lines.append(f"- {title}: {content} ({url})")
    return "\n".join(lines)


def research_agent(state: StartupState) -> dict[str, str]:
    idea = state["idea"]
    market = state["market_analysis"]
    query = f"market evidence competitors customer demand for: {idea}\nContext: {market}"

    results = get_search_tool().invoke({"query": query})
    return {"research_findings": format_results(results)}
