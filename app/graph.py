"""Advanced workflow with a bounded improvement loop."""

from langgraph.graph import END, START, StateGraph

from app.agents.business import business_agent
from app.agents.implementation import implementation_agent
from app.agents.improve import improve_agent
from app.agents.judge import judge_agent
from app.agents.market import market_agent
from app.agents.research import research_agent
from app.agents.risk import risk_agent
from app.state import StartupState

MAX_ITERATIONS = 3


def route_after_judge(state: StartupState) -> str:
    if state["verdict"] == "NO-GO" and state.get("iteration", 0) < MAX_ITERATIONS:
        return "improve"
    return "end"


# Data schema LangGraph manages between nodes.
builder = StateGraph(StartupState)

# Register functions without calling them here.
builder.add_node("market", market_agent)
builder.add_node("research", research_agent)
builder.add_node("risk", risk_agent)
builder.add_node("business", business_agent)
builder.add_node("implementation", implementation_agent)
builder.add_node("judge", judge_agent)
builder.add_node("improve", improve_agent)

# START and END are special markers, not agents or LLM calls.
builder.add_edge(START, "market")
builder.add_edge("market", "research")
builder.add_edge("research", "risk")
builder.add_edge("risk", "business")
builder.add_edge("business", "implementation")
builder.add_edge("implementation", "judge")
builder.add_conditional_edges("judge", route_after_judge, {"improve": "improve", "end": END})
builder.add_edge("improve", "market")

# Compile the description; execution starts only at graph.invoke(...).
graph = builder.compile()
