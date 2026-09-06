"""Improve a weak startup idea before another evaluation pass."""

from app.llm import get_llm
from app.state import StartupState


def improve_agent(state: StartupState) -> dict[str, str | int]:
    """Return an improved idea and increment the iteration counter."""
    idea = state["idea"]
    recommendation = state["recommendation"]
    iteration = state.get("iteration", 0) + 1

    messages = [
        (
            "system",
            "You improve startup ideas after a critical evaluation. "
            "Return a concise revised idea and explain what changed. "
            "Do not add fake traction, users, funding, statistics, or research. "
            "Keep the revised idea realistic and testable.",
        ),
        (
            "human",
            f"Original idea:\n{idea}\n\nJudge recommendation:\n{recommendation}",
        ),
    ]

    response = get_llm().invoke(messages)
    improved_idea = response.text.strip()
    if not improved_idea:
        raise ValueError("Improve Agent received an empty response.")

    return {
        "idea": improved_idea,
        "improvement_notes": recommendation,
        "iteration": iteration,
    }
