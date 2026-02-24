"""This module provides validation functions for the AI model's responses."""

import json
from pydantic import ValidationError
from models import SupportAnalysis, RiskLevel, SubIntent, PrimaryIntent


def valid_json(response: str) -> dict:
    """Validate that the response from the AI model is valid JSON and return it as a dictionary."""
    try:
        data = json.loads(response)
    except json.JSONDecodeError as e:
        raise ValueError("Invalid JSON response from model") from e
    return data


def parse_response(data: dict) -> SupportAnalysis:
    """Parse the AI model's response into a `SupportAnalysis` object."""
    try:
        return SupportAnalysis(**data)
    except Exception as e:
        raise ValueError(f"Invalid response format: {e}")


def apply_risk_overrides(query: str, analysis: SupportAnalysis) -> SupportAnalysis:
    """Apply rule-based overrides to the risk level and escalation requirement based on query content."""
    high_risk_indicators = ["emergency", "complaint", "legal threat", "fraud",
                            "identity theft", "ombudsman", "regulator", "escalate", "supervisor", "manager"]
    if any(high_risk_indicator in query.lower() for high_risk_indicator in high_risk_indicators):
        analysis.risk_level = RiskLevel.HIGH
        analysis.escalation_required = True
    return analysis


def adjust_confidence(analysis: SupportAnalysis) -> SupportAnalysis:
    """Adjust the confidence score based on the presence of secondary intents and sub-intents."""
    confidence = analysis.confidence_score

    if analysis.secondary_intent is not None:
        confidence -= 0.2

    if (
        analysis.secondary_sub_intent is not None
        and analysis.secondary_sub_intent != SubIntent.NULL
    ):
        confidence -= 0.1

    confidence = max(0.0, min(1.0, confidence))

    analysis.confidence_score = confidence
    analysis.manual_review_required = confidence < 0.6

    return analysis
