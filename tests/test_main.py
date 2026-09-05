import unittest
from unittest.mock import patch

from app.main import run_streamed_graph


class MainTests(unittest.TestCase):
    @patch("app.main.graph")
    def test_run_streamed_graph_accumulates_streamed_updates(self, graph):
        graph.stream.return_value = [
            {"market": {"market_analysis": "market result"}},
            {"risk": {"risk_analysis": "risk result"}},
            {"business": {"business_analysis": "business result"}},
            {
                "judge": {
                    "final_score": 70,
                    "verdict": "MAYBE",
                    "recommendation": "Run a pilot.",
                }
            },
        ]

        result = run_streamed_graph({"idea": "Scheduling assistant"})

        self.assertEqual(
            result,
            {
                "idea": "Scheduling assistant",
                "market_analysis": "market result",
                "risk_analysis": "risk result",
                "business_analysis": "business result",
                "final_score": 70,
                "verdict": "MAYBE",
                "recommendation": "Run a pilot.",
            },
        )
        graph.stream.assert_called_once_with({"idea": "Scheduling assistant"})


if __name__ == "__main__":
    unittest.main()
