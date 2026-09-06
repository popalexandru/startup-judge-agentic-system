"""FastAPI entrypoint for evaluating startup ideas."""

from pathlib import Path
from typing import Literal

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from app.graph import graph
from app.state import StartupState

FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"

app = FastAPI(title="Startup Judge Agentic System")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


class EvaluationRequest(BaseModel):
    idea: str = Field(min_length=1)

    @field_validator("idea")
    @classmethod
    def idea_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Startup idea must not be blank.")
        return stripped


class ResearchSourceResponse(BaseModel):
    title: str
    url: str
    summary: str


class EvaluationResponse(BaseModel):
    idea: str
    final_score: int = Field(ge=0, le=100)
    verdict: Literal["GO", "MAYBE", "NO-GO"]
    recommendation: str
    iteration: int = 0
    research_sources: list[ResearchSourceResponse] = Field(default_factory=list)


@app.get("/")
def index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/evaluate", response_model=EvaluationResponse)
def evaluate(request: EvaluationRequest) -> EvaluationResponse:
    initial_state: StartupState = {"idea": request.idea}
    final_state = graph.invoke(initial_state)

    return EvaluationResponse(
        idea=final_state["idea"],
        final_score=final_state["final_score"],
        verdict=final_state["verdict"],
        recommendation=final_state["recommendation"],
        iteration=final_state.get("iteration", 0),
        research_sources=final_state.get("research_sources", []),
    )
