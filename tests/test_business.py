import unittest
from unittest.mock import patch
from langchain_core.messages import AIMessage
from app.agents.business import business_agent


class BusinessTests(unittest.TestCase):
    @patch("app.agents.business.get_llm")
    def test_partial_update_and_input_preserved(self, get_llm):
        state = {"idea": "Idea", "market_analysis": "Market", "risk_analysis": "Risks"}
        before = state.copy()
        get_llm.return_value.invoke.return_value = AIMessage(content="Business")
        self.assertEqual(business_agent(state), {"business_analysis": "Business"})
        self.assertEqual(state, before)
        prompt = get_llm.return_value.invoke.call_args.args[0][-1][1]
        for value in state.values():
            self.assertIn(value, prompt)

    @patch("app.agents.business.get_llm")
    def test_empty_response_rejected(self, get_llm):
        get_llm.return_value.invoke.return_value = AIMessage(content=" ")
        with self.assertRaisesRegex(ValueError, "empty response"):
            business_agent({"idea": "Idea", "market_analysis": "Market", "risk_analysis": "Risks"})
