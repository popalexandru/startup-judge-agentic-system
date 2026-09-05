"""Node contract, without real API calls or keys."""

import unittest
from unittest.mock import patch

from langchain_core.messages import AIMessage

from app.agents.market import market_agent


class MarketAgentTests(unittest.TestCase):
    @patch("app.agents.market.get_llm")
    def test_returns_only_analysis_without_mutating_state(self, get_llm):
        state = {"idea": "Barbershop scheduling assistant", "risk_analysis": "Keep this"}
        before = state.copy()
        get_llm.return_value.invoke.return_value = AIMessage(content="Mock analysis")

        update = market_agent(state)

        self.assertEqual(update, {"market_analysis": "Mock analysis"})
        self.assertEqual(state, before)
        get_llm.return_value.invoke.assert_called_once()
        messages = get_llm.return_value.invoke.call_args.args[0]
        self.assertEqual(messages[-1], ("human", state["idea"]))

    @patch("app.agents.market.get_llm")
    def test_rejects_blank_idea_before_creating_client(self, get_llm):
        with self.assertRaisesRegex(ValueError, "non-empty"):
            market_agent({"idea": "  "})
        get_llm.assert_not_called()

    @patch("app.agents.market.get_llm")
    def test_rejects_empty_response(self, get_llm):
        get_llm.return_value.invoke.return_value = AIMessage(content="  ")
        with self.assertRaisesRegex(ValueError, "empty response"):
            market_agent({"idea": "Barbershop scheduling assistant"})

    @patch("app.agents.market.get_llm")
    def test_api_failure_propagates_without_state_changes(self, get_llm):
        state = {"idea": "Barbershop scheduling assistant"}
        before = state.copy()
        get_llm.return_value.invoke.side_effect = RuntimeError("API unavailable")
        with self.assertRaisesRegex(RuntimeError, "API unavailable"):
            market_agent(state)
        self.assertEqual(state, before)


if __name__ == "__main__":
    unittest.main()
