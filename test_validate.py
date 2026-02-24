"""test module for validate.py"""

import pytest
from validate import valid_json, parse_response, apply_risk_overrides, adjust_confidence
from models import SupportAnalysis, RiskLevel, SubIntent, PrimaryIntent


@pytest.fixture
def sample_model_output() -> str:
    """Provides a sample JSON response from the AI model for testing."""
    return """
    {
        "primary_intent": "account_access",
        "primary_sub_intent": "reset_pin",
        "secondary_intent": null,
        "secondary_sub_intent": null,
        "key_information": ["customer cannot access account", "forgotten PIN"],
        "risk_level": "MEDIUM",
        "escalation_required": false,
        "confidence_score": 0.85,
        "manual_review_required": false,
        "reasoning_summary": "The customer's main issue is accessing their account, which is best captured by the 'account_access' intent and 'reset_pin' sub-intent.",
        "suggested_next_steps": ["Verify customer's identity", "Guide customer through PIN reset process"]
    }
    """



def test_valid_json(sample_model_output):
    """Test that valid_json correctly parses a valid JSON string."""
    data = valid_json(sample_model_output)
    assert isinstance(data, dict)
    assert data["primary_intent"] == "account_access"
    assert data["confidence_score"] == 0.85


def test_invalid_json():
    """Test that valid_json raises a ValueError for invalid JSON."""
    invalid_json = "{invalid: json, missing: quotes}"
    with pytest.raises(ValueError):
        valid_json(invalid_json)


def test_parse_response(sample_model_output):
    """Test that parse_response correctly converts a dictionary to a SupportAnalysis object."""
    data = valid_json(sample_model_output)
    analysis = parse_response(data)
    assert isinstance(analysis, SupportAnalysis)

def test_parse_response_invalid_format():
    """Test that parse_response raises a ValueError for invalid response format."""
    invalid_data = {"unexpected_field": "unexpected_value"}
    with pytest.raises(ValueError):
        parse_response(invalid_data)


def test_apply_risk_overrides(sample_model_output):
    """Test that apply_risk_overrides correctly updates the risk level and escalation requirement."""
    data = valid_json(sample_model_output)
    analysis = parse_response(data)
    query = "I want to escalate this issue to a supervisor because I am very upset about my account access problems."
    updated_analysis = apply_risk_overrides(query, analysis)
    assert updated_analysis.risk_level == RiskLevel.HIGH
    assert updated_analysis.escalation_required is True


def test_apply_risk_overrides_no_change(sample_model_output):
    """Test that apply_risk_overrides does not change the risk level or escalation requirement when no indicators are present."""
    data = valid_json(sample_model_output)
    analysis = parse_response(data)
    query = "I just have a question about my account balance."
    updated_analysis = apply_risk_overrides(query, analysis)
    assert updated_analysis.risk_level == analysis.risk_level
    assert updated_analysis.escalation_required == analysis.escalation_required

def test_adjust_confidence(sample_model_output):
    """Test that adjust_confidence correctly adjusts the confidence score and manual review requirement."""

    data = valid_json(sample_model_output)
    analysis = parse_response(data)
    analysis.secondary_intent = PrimaryIntent.payments_and_funds
    analysis.secondary_sub_intent = SubIntent.payment_declined

    confidence_before = analysis.confidence_score
    assert confidence_before == 0.85
    assert analysis.manual_review_required is False

    updated_analysis = adjust_confidence(analysis)

    assert updated_analysis.confidence_score < confidence_before
    assert updated_analysis.manual_review_required is True


def test_adjust_confidence_no_sub_intents(sample_model_output):
    """Test that adjust_confidence does not adjust the confidence score when no secondary intents or sub-intents are present."""
    data = valid_json(sample_model_output)
    analysis = parse_response(data)

    confidence_before = analysis.confidence_score
    assert confidence_before == 0.85
    assert analysis.manual_review_required is False

    updated_analysis = adjust_confidence(analysis)

    assert updated_analysis.confidence_score == confidence_before
    assert updated_analysis.manual_review_required is False
