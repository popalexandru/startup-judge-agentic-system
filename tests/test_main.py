import unittest
from unittest.mock import patch

from app.main import print_route_after_judge, run_streamed_graph


class MainTests(unittest.TestCase):
    @patch("app.main.graph")
    def test_run_streamed_graph_accumulates_streamed_updates(self, graph):
        graph.stream.return_value = [
            {"market": {"market_analysis": "market result"}},
            {"research": {"research_findings": "research result"}},
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
                "research_findings": "research result",
                "risk_analysis": "risk result",
                "business_analysis": "business result",
                "final_score": 70,
                "verdict": "MAYBE",
                "recommendation": "Run a pilot.",
            },
        )
        graph.stream.assert_called_once_with({"idea": "Scheduling assistant"})

    @patch("app.main.console.print")
    def test_print_route_after_judge_for_terminal_verdict(self, print_mock):
        print_route_after_judge({"idea": "Idea", "verdict": "MAYBE"})
        print_mock.assert_called_once_with(
            "[bold yellow][ROUTE][/bold yellow] "
            "[green]MAYBE[/green] -> [yellow]end[/yellow]"
        )

    @patch("app.main.console.print")
    def test_print_route_after_judge_for_improvement_route(self, print_mock):
        print_route_after_judge({"idea": "Idea", "verdict": "NO-GO", "iteration": 1})
        print_mock.assert_called_once_with(
            "[bold yellow][ROUTE][/bold yellow] "
            "[red]NO-GO[/red] at iteration 1/3 -> [yellow]improve[/yellow]"
        )


if __name__ == "__main__":
    unittest.main()
