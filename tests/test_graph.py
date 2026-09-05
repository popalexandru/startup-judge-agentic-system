"""Real V1 graph with mocked LLMs: order, data transfer, and final state."""
import unittest
from unittest.mock import patch
from langchain_core.messages import AIMessage
from app.agents.judge import JudgeOutput
from app.graph import graph


class GraphTests(unittest.TestCase):
    def setUp(self):
        self.clients = {}
        self.order = []
        for name in ("market", "risk", "business", "judge"):
            patcher = patch(f"app.agents.{name}.get_llm")
            self.clients[name] = patcher.start().return_value
            self.addCleanup(patcher.stop)
        self.output = JudgeOutput(final_score=65, verdict="MAYBE", recommendation="Test a pilot.")
        for name in ("market", "risk", "business"):
            def respond(messages, name=name):
                self.order.append(name)
                return AIMessage(content=f"{name} result")
            self.clients[name].invoke.side_effect = respond
        def judge_response(messages):
            self.order.append("judge")
            return self.output
        self.clients["judge"].with_structured_output.return_value.invoke.side_effect = judge_response

    def test_full_flow_transfers_results_in_order(self):
        initial = {"idea": "Barbershop scheduling assistant"}
        result = graph.invoke(initial)
        self.assertEqual(self.order, ["market", "risk", "business", "judge"])
        self.assertEqual(initial, {"idea": "Barbershop scheduling assistant"})
        self.assertEqual(result, {**initial, "market_analysis": "market result",
            "risk_analysis": "risk result", "business_analysis": "business result",
            **self.output.model_dump()})
        for name, required in (("risk", ["market"]), ("business", ["market", "risk"]),
                               ("judge", ["market", "risk", "business"])):
            client = self.clients[name]
            invoke = client.with_structured_output.return_value.invoke if name == "judge" else client.invoke
            invoke.assert_called_once()
            prompt = invoke.call_args.args[0][-1][1]
            self.assertIn("Barbershop scheduling assistant", prompt)
            for source in required:
                self.assertIn(f"{source} result", prompt)

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
