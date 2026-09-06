# Startup Judge Agentic System

Startup Judge Agentic System is the advanced version of the Startup Judge portfolio project.

It starts from a clean LangGraph V1 workflow and evolves into a more realistic agentic system with streaming progress, conditional routing, bounded research loops, tool use, an API, and a dark product-style interface.

```text
START -> Market -> Research -> Risk -> Business -> Implementation -> Judge
                                                                   |   |
                                                                   |   v
                                                                   |  END
                                                                   v
                                                                Improve -> Market
```

## Current Baseline

The current implementation is the V1 sequential graph:

- typed workflow state with `StartupState`
- six focused LangGraph analysis nodes
- Tavily-powered web research between Market and Risk
- visible research sources in the final CLI output
- practical MVP implementation planning with rough time/cost level
- partial state updates between agents
- structured Judge output with Pydantic
- deterministic verdict mapping from score
- streamed CLI execution with `graph.stream(...)`
- colored terminal output with Rich
- FastAPI backend with `POST /evaluate`
- dark themed frontend served by the FastAPI app
- conditional routing after Judge
- bounded improvement loop with a maximum of 3 iterations
- mocked LLM tests

This baseline is intentionally simple so each advanced capability can be added and understood one step at a time.

## Planned Evolution

- persist evaluations and previous runs

## Workflow

| Agent | Reads | Produces |
| --- | --- | --- |
| Market | `idea` | `market_analysis` |
| Research | `idea`, `market_analysis` | `research_findings`, `research_sources` |
| Risk | `idea`, `market_analysis`, `research_findings` | `risk_analysis` |
| Business | `idea`, `market_analysis`, `research_findings`, `risk_analysis` | `business_analysis` |
| Implementation | `idea`, all previous analyses | `implementation_plan` |
| Judge | `idea`, all analyses, `implementation_plan` | `final_score`, `verdict`, `recommendation` |
| Improve | `idea`, `recommendation`, `iteration` | `idea`, `improvement_notes`, `iteration` |

After Judge runs, the graph routes conditionally:

- scores `70-100` map to `GO`
- scores `40-69` map to `MAYBE`
- scores `0-39` map to `NO-GO`
- `GO` or `MAYBE` ends the workflow
- `NO-GO` routes to Improve while `iteration < 3`
- after 3 improvement attempts, the workflow ends even if the verdict is still `NO-GO`

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Add your OpenAI API key to `.env`:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4.1-mini
TAVILY_API_KEY=your_tavily_api_key_here
```

## Run

CLI:

```bash
python -m app.main "AI assistant for barbershop scheduling"
```

During execution, the CLI prints each streamed graph update:

```text
[STREAM] market -> market_analysis
[STREAM] research -> research_findings, research_sources
[STREAM] risk -> risk_analysis
[STREAM] business -> business_analysis
[STREAM] implementation -> implementation_plan
[STREAM] judge -> final_score, verdict, recommendation
[ROUTE] MAYBE -> end

Research Sources
1. Example source title
   https://example.com
```

If Judge returns `NO-GO` and the loop still has attempts left, the CLI shows the retry route:

```text
[ROUTE] NO-GO at iteration 0/3 -> improve
[STREAM] improve -> idea, improvement_notes, iteration
```

API:

```bash
python -m uvicorn app.api:app --reload
```

Open the web interface:

```text
http://127.0.0.1:8000/
```

Or call the API directly:

```bash
curl -X POST http://127.0.0.1:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{"idea":"AI assistant for barbershop scheduling"}'
```

The API also exposes:

```text
GET /health
POST /evaluate
```

## Tests

```bash
python -m unittest discover -s tests -v
```

The tests mock LLM calls and verify state updates, graph order, streamed update accumulation, API responses, implementation planning, conditional routing, bounded loops, error propagation, and structured Judge validation.

## Related Repository

The simpler foundations-only version lives in:

https://github.com/popalexandru/startup-judge-langgraph-basics
