"""Real Pydantic validation and the Judge node contract."""
import unittest
from unittest.mock import patch
from pydantic import ValidationError
from app.agents.judge import JudgeOutput, judge_agent


class JudgeTests(unittest.TestCase):
    def test_valid_boundaries_and_verdicts(self):
        for score in (0, 100):
            for verdict in ("GO", "MAYBE", "NO-GO"):
                JudgeOutput(final_score=score, verdict=verdict, recommendation="Pilot")

    def test_rejects_invalid_outputs(self):
        valid = {"final_score": 50, "verdict": "MAYBE", "recommendation": "Pilot"}
        for update in ({"final_score": -1}, {"final_score": 101}, {"final_score": 2.5},
                       {"final_score": True}, {"verdict": "APPROVED"}, {"recommendation": "   "}):
            with self.subTest(update=update), self.assertRaises(ValidationError):
                JudgeOutput(**{**valid, **update})
        with self.assertRaises(ValidationError):
            JudgeOutput(final_score=50, verdict="MAYBE")

    @patch("app.agents.judge.get_llm")
    def test_returns_validated_update_without_mutation(self, get_llm):
        state = {"idea": "Idea", "market_analysis": "Market", "research_findings": "Research", "risk_analysis": "Risks",
                 "business_analysis": "Business"}
        before = state.copy()
        output = JudgeOutput(final_score=60, verdict="MAYBE", recommendation="Pilot")
        get_llm.return_value.with_structured_output.return_value.invoke.return_value = output
        self.assertEqual(judge_agent(state), output.model_dump())
        self.assertEqual(state, before)
        get_llm.return_value.with_structured_output.assert_called_once_with(
            JudgeOutput, method="json_schema", strict=True)

    @patch("app.agents.judge.get_llm")
    def test_validation_failure_does_not_produce_update(self, get_llm):
        def invalid_response(messages):
            return JudgeOutput(final_score=101, verdict="GO", recommendation="Pilot")
        get_llm.return_value.with_structured_output.return_value.invoke.side_effect = invalid_response
        state = {"idea": "Idea", "market_analysis": "Market", "research_findings": "Research", "risk_analysis": "Risks",
                 "business_analysis": "Business"}
        before = state.copy()
        with self.assertRaises(ValidationError):
            judge_agent(state)
        self.assertEqual(state, before)
