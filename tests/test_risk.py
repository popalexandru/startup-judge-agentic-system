"""Risk contract, without API calls."""

import unittest
from unittest.mock import patch

from langchain_core.messages import AIMessage

from app.agents.risk import risk_agent


class RiskAgentTests(unittest.TestCase):
    @patch("app.agents.risk.get_llm")
    def test_returns_partial_update_without_mutation(self, get_llm):
        state = {"idea": "Barbershops", "market_analysis": "Market hypothesis"}
        before = state.copy()
        get_llm.return_value.invoke.return_value = AIMessage(content="Risks")
        self.assertEqual(risk_agent(state), {"risk_analysis": "Risks"})
        self.assertEqual(state, before)
        prompt = get_llm.return_value.invoke.call_args.args[0][-1][1]
        self.assertIn(state["idea"], prompt)
        self.assertIn(state["market_analysis"], prompt)

    @patch("app.agents.risk.get_llm")
    def test_missing_market_result_fails_before_llm(self, get_llm):
        with self.assertRaises(KeyError):
            risk_agent({"idea": "Barbershops"})
        get_llm.assert_not_called()

    @patch("app.agents.risk.get_llm")
    def test_blank_market_result_fails_before_llm(self, get_llm):
        with self.assertRaisesRegex(ValueError, "non-empty Market analysis"):
            risk_agent({"idea": "Barbershops", "market_analysis": " "})
        get_llm.assert_not_called()

    @patch("app.agents.risk.get_llm")
    def test_empty_response_does_not_modify_state(self, get_llm):
        state = {"idea": "Barbershops", "market_analysis": "Hypothesis"}
        before = state.copy()
        get_llm.return_value.invoke.return_value = AIMessage(content="")
        with self.assertRaisesRegex(ValueError, "empty response"):
            risk_agent(state)
        self.assertEqual(state, before)


if __name__ == "__main__":
    unittest.main()
