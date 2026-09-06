import unittest
from unittest.mock import patch

from langchain_core.messages import AIMessage

from app.agents.improve import improve_agent


class ImproveTests(unittest.TestCase):
    @patch("app.agents.improve.get_llm")
    def test_returns_improved_idea_and_increments_iteration(self, get_llm):
        state = {
            "idea": "Generic scheduling app",
            "recommendation": "Narrow the target segment.",
            "iteration": 1,
        }
        before = state.copy()
        get_llm.return_value.invoke.return_value = AIMessage(
            content="Scheduling assistant for independent barbershops"
        )

        update = improve_agent(state)

        self.assertEqual(
            update,
            {
                "idea": "Scheduling assistant for independent barbershops",
                "improvement_notes": "Narrow the target segment.",
                "iteration": 2,
            },
        )
        self.assertEqual(state, before)

    @patch("app.agents.improve.get_llm")
    def test_empty_response_rejected(self, get_llm):
        get_llm.return_value.invoke.return_value = AIMessage(content=" ")
        with self.assertRaisesRegex(ValueError, "empty response"):
            improve_agent({"idea": "Idea", "recommendation": "Improve it."})


if __name__ == "__main__":
    unittest.main()
