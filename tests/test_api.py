import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.api import app

client = TestClient(app)


class ApiTests(unittest.TestCase):
    def test_homepage_serves_frontend(self):
        response = client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Startup Judge", response.text)
        self.assertIn('data-step="market"', response.text)
        self.assertIn('data-step="implementation"', response.text)
        self.assertIn('id="agent-dialog"', response.text)

    def test_static_assets_are_served(self):
        response = client.get("/static/app.js")

        self.assertEqual(response.status_code, 200)
        self.assertIn("fetch(\"/evaluate\"", response.text)

    def test_health(self):
        response = client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    @patch("app.api.graph")
    def test_evaluate_returns_public_response(self, graph):
        graph.invoke.return_value = {
            "idea": "Barbershop scheduling assistant",
            "market_analysis": "Market analysis.",
            "research_findings": "Research findings.",
            "risk_analysis": "Risk analysis.",
            "business_analysis": "Business analysis.",
            "implementation_plan": "Implementation plan.",
            "final_score": 72,
            "verdict": "GO",
            "recommendation": "Run a pilot.",
            "iteration": 1,
            "research_sources": [
                {
                    "title": "Booking software market",
                    "url": "https://example.com",
                    "summary": "Market context.",
                }
            ],
        }

        response = client.post("/evaluate", json={"idea": "  Barbershop scheduling assistant  "})

        self.assertEqual(response.status_code, 200)
        graph.invoke.assert_called_once_with({"idea": "Barbershop scheduling assistant"})
        self.assertEqual(
            response.json(),
            {
                "idea": "Barbershop scheduling assistant",
                "final_score": 72,
                "verdict": "GO",
                "recommendation": "Run a pilot.",
                "iteration": 1,
                "research_sources": [
                    {
                        "title": "Booking software market",
                        "url": "https://example.com",
                        "summary": "Market context.",
                    }
                ],
                "agent_outputs": {
                    "market": "Market analysis.",
                    "research": "Research findings.",
                    "risk": "Risk analysis.",
                    "business": "Business analysis.",
                    "implementation": "Implementation plan.",
                    "judge": "Run a pilot.",
                },
            },
        )

    @patch("app.api.graph")
    def test_blank_idea_is_rejected_before_graph_runs(self, graph):
        response = client.post("/evaluate", json={"idea": "   "})

        self.assertEqual(response.status_code, 422)
        graph.invoke.assert_not_called()


if __name__ == "__main__":
    unittest.main()
