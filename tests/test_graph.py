"""Graph behavior with mocked LLMs: order, routing, and final state."""
import unittest
from unittest.mock import patch
from langchain_core.messages import AIMessage
from app.agents.judge import JudgeLLMOutput
from app.graph import MAX_ITERATIONS, graph, route_after_judge


class GraphTests(unittest.TestCase):
    def setUp(self):
        self.clients = {}
        self.order = []
        for name in ("market", "risk", "business", "judge", "improve"):
            patcher = patch(f"app.agents.{name}.get_llm")
            self.clients[name] = patcher.start().return_value
            self.addCleanup(patcher.stop)
        self.output = JudgeLLMOutput(final_score=65, recommendation="Test a pilot.")
        for name in ("market", "risk", "business"):
            def respond(messages, name=name):
                self.order.append(name)
                return AIMessage(content=f"{name} result")
            self.clients[name].invoke.side_effect = respond
        search_patcher = patch("app.agents.research.get_search_tool")
        self.search_tool = search_patcher.start().return_value
        self.addCleanup(search_patcher.stop)
        self.search_tool.invoke.side_effect = self.research_response
        def judge_response(messages):
            self.order.append("judge")
            return self.output
        self.clients["judge"].with_structured_output.return_value.invoke.side_effect = judge_response

        def improve_response(messages):
            self.order.append("improve")
            return AIMessage(content="Improved barbershop scheduling assistant")
        self.clients["improve"].invoke.side_effect = improve_response

    def research_response(self, query):
        self.order.append("research")
        return {"results": [{"title": "Research", "url": "https://example.com", "content": "research result"}]}

    def test_full_flow_transfers_results_in_order(self):
        initial = {"idea": "Barbershop scheduling assistant"}
        result = graph.invoke(initial)
        self.assertEqual(self.order, ["market", "research", "risk", "business", "judge"])
        self.assertEqual(initial, {"idea": "Barbershop scheduling assistant"})
        self.assertEqual(result, {**initial, "market_analysis": "market result",
            "research_findings": "- Research: research result (https://example.com)",
            "risk_analysis": "risk result", "business_analysis": "business result",
            "final_score": 65, "verdict": "MAYBE", "recommendation": "Test a pilot."})
        for name, required in (("risk", ["market", "research"]), ("business", ["market", "research", "risk"]),
                               ("judge", ["market", "research", "risk", "business"])):
            client = self.clients[name]
            invoke = client.with_structured_output.return_value.invoke if name == "judge" else client.invoke
            invoke.assert_called_once()
            prompt = invoke.call_args.args[0][-1][1]
            self.assertIn("Barbershop scheduling assistant", prompt)
            for source in required:
                expected = "research result" if source == "research" else f"{source} result"
                self.assertIn(expected, prompt)

    def test_existing_analysis_is_replaced(self):
        result = graph.invoke({"idea": "Barbershop scheduling assistant", "market_analysis": "Old"})
        self.assertEqual(result["market_analysis"], "market result")
        self.assertEqual(result["idea"], "Barbershop scheduling assistant")

    def test_invocations_do_not_share_context(self):
        graph.invoke({"idea": "First idea"})
        result = graph.invoke({"idea": "Second idea"})
        self.assertEqual(result["idea"], "Second idea")
        prompt = self.clients["market"].invoke.call_args.args[0][-1][1]
        self.assertEqual(prompt, "Second idea")

    def test_failure_prevents_downstream_execution(self):
        self.clients["risk"].invoke.side_effect = RuntimeError("Risk failed")
        with self.assertRaisesRegex(RuntimeError, "Risk failed"):
            graph.invoke({"idea": "Barbershop scheduling assistant"})
        self.clients["business"].invoke.assert_not_called()
        self.clients["judge"].with_structured_output.assert_not_called()

    def test_no_go_routes_to_improvement_then_retries(self):
        outputs = [
            JudgeLLMOutput(final_score=25, recommendation="Narrow the target segment."),
            JudgeLLMOutput(final_score=70, recommendation="Test a pilot."),
        ]

        def judge_response(messages):
            self.order.append("judge")
            return outputs.pop(0)

        self.clients["judge"].with_structured_output.return_value.invoke.side_effect = judge_response

        result = graph.invoke({"idea": "Generic scheduling app"})

        self.assertEqual(
            self.order,
            [
                "market", "research", "risk", "business", "judge", "improve",
                "market", "research", "risk", "business", "judge",
            ],
        )
        self.assertEqual(result["idea"], "Improved barbershop scheduling assistant")
        self.assertEqual(result["iteration"], 1)
        self.assertEqual(result["improvement_notes"], "Narrow the target segment.")
        self.assertEqual(result["verdict"], "GO")

    def test_no_go_stops_after_max_iterations(self):
        self.output = JudgeLLMOutput(final_score=20, recommendation="Still too broad.")

        result = graph.invoke({"idea": "Generic scheduling app"})

        self.assertEqual(self.order.count("improve"), MAX_ITERATIONS)
        self.assertEqual(result["iteration"], MAX_ITERATIONS)
        self.assertEqual(result["verdict"], "NO-GO")

    def test_route_after_judge(self):
        self.assertEqual(route_after_judge({"idea": "Idea", "verdict": "GO"}), "end")
        self.assertEqual(route_after_judge({"idea": "Idea", "verdict": "MAYBE"}), "end")
        self.assertEqual(route_after_judge({"idea": "Idea", "verdict": "NO-GO"}), "improve")
        self.assertEqual(
            route_after_judge({"idea": "Idea", "verdict": "NO-GO", "iteration": MAX_ITERATIONS}),
            "end",
        )
