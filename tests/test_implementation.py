"""Implementation agent contract."""

import unittest
from unittest.mock import patch

from langchain_core.messages import AIMessage

from app.agents.implementation import implementation_agent


class ImplementationTests(unittest.TestCase):
    @patch("app.agents.implementation.get_llm")
    def test_returns_implementation_plan_without_mutation(self, get_llm):
        state = {
            "idea": "Idea",
            "market_analysis": "Market",
            "research_findings": "Research",
            "risk_analysis": "Risks",
            "business_analysis": "Business",
        }
        before = state.copy()
        get_llm.return_value.invoke.return_value = AIMessage(content="MVP plan")

        self.assertEqual(implementation_agent(state), {"implementation_plan": "MVP plan"})
        self.assertEqual(state, before)

        prompt = get_llm.return_value.invoke.call_args.args[0][-1][1]
        for expected in state.values():
            self.assertIn(expected, prompt)

    @patch("app.agents.implementation.get_llm")
    def test_empty_response_is_rejected(self, get_llm):
        get_llm.return_value.invoke.return_value = AIMessage(content="   ")
        state = {
            "idea": "Idea",
            "market_analysis": "Market",
            "research_findings": "Research",
            "risk_analysis": "Risks",
            "business_analysis": "Business",
        }

        with self.assertRaisesRegex(ValueError, "empty response"):
            implementation_agent(state)


if __name__ == "__main__":
    unittest.main()
