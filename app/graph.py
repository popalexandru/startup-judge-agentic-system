"""First workflow: V1: START -> Market -> Risk -> Business -> Judge -> END."""

from langgraph.graph import END, START, StateGraph

from app.agents.business import business_agent
from app.agents.judge import judge_agent
from app.agents.market import market_agent
from app.agents.risk import risk_agent
from app.state import StartupState


# Data schema LangGraph manages between nodes.
builder = StateGraph(StartupState)

# Register functions without calling them here.
builder.add_node("market", market_agent)
builder.add_node("risk", risk_agent)
builder.add_node("business", business_agent)
builder.add_node("judge", judge_agent)

# START and END are special markers, not agents or LLM calls.
builder.add_edge(START, "market")
builder.add_edge("market", "risk")
builder.add_edge("risk", "business")
builder.add_edge("business", "judge")
builder.add_edge("judge", END)

# Compile the description; execution starts only at graph.invoke(...).
graph = builder.compile()
