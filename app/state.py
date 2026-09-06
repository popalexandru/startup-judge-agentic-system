"""Data for one workflow run; nodes return updates for these fields."""

from typing import Literal

from typing_extensions import NotRequired, TypedDict


class StartupState(TypedDict):
    # Provided by the user when the workflow starts.
    idea: str

    # Initially absent; each agent adds its own result.
    market_analysis: NotRequired[str]
    research_findings: NotRequired[str]
    risk_analysis: NotRequired[str]
    business_analysis: NotRequired[str]
    improvement_notes: NotRequired[str]
    iteration: NotRequired[int]

    # Produced by Judge; validated by JudgeOutput.
    final_score: NotRequired[int]
    verdict: NotRequired[Literal["GO", "MAYBE", "NO-GO"]]
    recommendation: NotRequired[str]
