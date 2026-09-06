import unittest
from unittest.mock import patch

from app.agents.research import format_results, research_agent


class ResearchTests(unittest.TestCase):
    def test_format_results(self):
        self.assertEqual(
            format_results(
                {
                    "results": [
                        {
                            "title": "Market report",
                            "url": "https://example.com",
                            "content": "Useful summary.",
                        }
                    ]
                }
            ),
            "- Market report: Useful summary. (https://example.com)",
        )

    def test_format_results_handles_empty_results(self):
        self.assertEqual(format_results({"results": []}), "No relevant web results found.")

    @patch("app.agents.research.get_search_tool")
    def test_research_agent_returns_findings(self, get_search_tool):
        get_search_tool.return_value.invoke.return_value = {
            "results": [
                {
                    "title": "Competitor",
                    "url": "https://example.com/competitor",
                    "content": "A competitor exists.",
                }
            ]
        }

        update = research_agent(
            {
                "idea": "Barbershop scheduling assistant",
                "market_analysis": "Small shops need booking automation.",
            }
        )

        self.assertIn("Competitor", update["research_findings"])
        get_search_tool.return_value.invoke.assert_called_once()


if __name__ == "__main__":
    unittest.main()
