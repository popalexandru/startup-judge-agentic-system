"""Real Pydantic validation and the Judge node contract."""
import unittest
from unittest.mock import patch
from pydantic import ValidationError
from app.agents.judge import JudgeLLMOutput, judge_agent, verdict_from_score


class JudgeTests(unittest.TestCase):
    def test_verdict_from_score(self):
        for score, verdict in (
            (0, "NO-GO"),
            (39, "NO-GO"),
            (40, "MAYBE"),
            (69, "MAYBE"),
            (70, "GO"),
            (100, "GO"),
        ):
            with self.subTest(score=score):
                self.assertEqual(verdict_from_score(score), verdict)

    def test_rejects_invalid_llm_outputs(self):
        valid = {"final_score": 50, "recommendation": "Pilot"}
        for update in ({"final_score": -1}, {"final_score": 101}, {"final_score": 2.5},
                       {"final_score": True}, {"verdict": "MAYBE"}, {"recommendation": "   "}):
            with self.subTest(update=update), self.assertRaises(ValidationError):
                JudgeLLMOutput(**{**valid, **update})
        with self.assertRaises(ValidationError):
            JudgeLLMOutput(final_score=50)

    @patch("app.agents.judge.get_llm")
    def test_returns_validated_update_without_mutation(self, get_llm):
        state = {"idea": "Idea", "market_analysis": "Market", "research_findings": "Research", "risk_analysis": "Risks",
                 "business_analysis": "Business"}
        before = state.copy()
        output = JudgeLLMOutput(final_score=25, recommendation="Pilot")
        get_llm.return_value.with_structured_output.return_value.invoke.return_value = output
        self.assertEqual(
            judge_agent(state),
            {"final_score": 25, "verdict": "NO-GO", "recommendation": "Pilot"},
        )
        self.assertEqual(state, before)
        get_llm.return_value.with_structured_output.assert_called_once_with(
            JudgeLLMOutput, method="json_schema", strict=True)

    @patch("app.agents.judge.get_llm")
    def test_validation_failure_does_not_produce_update(self, get_llm):
        def invalid_response(messages):
            return JudgeLLMOutput(final_score=101, recommendation="Pilot")
        get_llm.return_value.with_structured_output.return_value.invoke.side_effect = invalid_response
        state = {"idea": "Idea", "market_analysis": "Market", "research_findings": "Research", "risk_analysis": "Risks",
                 "business_analysis": "Business"}
        before = state.copy()
        with self.assertRaises(ValidationError):
            judge_agent(state)
        self.assertEqual(state, before)
