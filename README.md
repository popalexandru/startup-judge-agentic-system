# Startup Judge Agentic System

Startup Judge Agentic System is the advanced version of the Startup Judge portfolio project.

It starts from a clean LangGraph V1 workflow and evolves into a more realistic agentic system with streaming progress, conditional routing, bounded research loops, tool use, and eventually an API or product interface.

```text
START -> Market -> Risk -> Business -> Judge -> END
```

## Current Baseline

The current implementation is the V1 sequential graph:

- typed workflow state with `StartupState`
- four focused LangGraph nodes
- partial state updates between agents
- structured Judge output with Pydantic
- streamed CLI execution with `graph.stream(...)`
- mocked LLM tests

This baseline is intentionally simple so each advanced capability can be added and understood one step at a time.

## Planned Evolution

- add conditional routing based on Judge uncertainty
- run a bounded improvement loop with a maximum number of iterations
- add a web research tool for evidence-aware analysis
- expose the workflow through an API
- add a lightweight frontend for portfolio demos
- persist evaluations and previous runs

## Workflow

| Agent | Reads | Produces |
| --- | --- | --- |
| Market | `idea` | `market_analysis` |
| Risk | `idea`, `market_analysis` | `risk_analysis` |
| Business | `idea`, `market_analysis`, `risk_analysis` | `business_analysis` |
| Judge | `idea`, all analyses | `final_score`, `verdict`, `recommendation` |

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
```

## Run

```bash
python -m app.main "AI assistant for barbershop scheduling"
```

During execution, the CLI prints each streamed graph update:

```text
[STREAM] market -> market_analysis
[STREAM] risk -> risk_analysis
[STREAM] business -> business_analysis
[STREAM] judge -> final_score, verdict, recommendation
```

## Tests

```bash
python -m unittest discover -s tests -v
```

The tests mock LLM calls and verify state updates, graph order, streamed update accumulation, error propagation, and structured Judge validation.

## Related Repository

The simpler foundations-only version lives in:

https://github.com/popalexandru/startup-judge-langgraph-basics
