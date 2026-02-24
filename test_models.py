# pylint skip-file
"""test suite for models.py"""

from models import PrimaryIntent, SubIntent, RiskLevel, SupportAnalysis
from pydantic import ValidationError
import pytest


@pytest.fixture
def support_analysis_data():
    return {
        "primary_intent": PrimaryIntent.account_access,
        "primary_sub_intent": SubIntent.reset_pin,
        "secondary_intent": None,
        "secondary_sub_intent": None,
        "key_information": ["User forgot PIN"],
        "risk_level": RiskLevel.LOW,
        "escalation_required": False,
        "confidence_score": 0.9,
        "manual_review_required": False,
        "suggested_next_steps": ["Send PIN reset link"],
    }


@pytest.fixture
def invalid_primary_intent_support_analysis_data(support_analysis_data):
    data = support_analysis_data.copy()
    data["primary_intent"] = "invalid_intent"
    return data


@pytest.fixture
def invalid_primary_sub_intent_support_analysis_data(support_analysis_data):
    data = support_analysis_data.copy()
    data["primary_sub_intent"] = "invalid_sub_intent"
    return data


def test_valid_support_analysis(support_analysis_data):
    analysis = SupportAnalysis(**support_analysis_data)
    assert analysis.primary_intent == PrimaryIntent.account_access
    assert analysis.primary_sub_intent == SubIntent.reset_pin
    assert analysis.confidence_score == 0.9
    assert analysis.manual_review_required == False
    assert analysis.suggested_next_steps == ["Send PIN reset link"]
    assert analysis.primary_sub_intent == SubIntent.reset_pin


def test_invalid_primary_intent(invalid_primary_intent_support_analysis_data):
    with pytest.raises(ValidationError):
        SupportAnalysis(**invalid_primary_intent_support_analysis_data)


def test_invalid_primary_sub_intent(invalid_primary_sub_intent_support_analysis_data):
    with pytest.raises(ValidationError):
        SupportAnalysis(**invalid_primary_sub_intent_support_analysis_data)


def test_null_secondary_intent(support_analysis_data):
    analysis = SupportAnalysis(**support_analysis_data)
    assert analysis.secondary_intent is None
    assert analysis.secondary_sub_intent is None


def test_secondary_sub_intent_without_secondary_intent(support_analysis_data):
    data = support_analysis_data.copy()
    data["secondary_sub_intent"] = SubIntent.reset_pin
    with pytest.raises(ValidationError):
        SupportAnalysis(**data)


def test_high_risk_without_escalation(support_analysis_data):
    data = support_analysis_data.copy()
    data["risk_level"] = RiskLevel.HIGH
    with pytest.raises(ValidationError):
        SupportAnalysis(**data)


def test_low_confidence_without_manual_review(support_analysis_data):
    data = support_analysis_data.copy()
    data["confidence_score"] = 0.4
    with pytest.raises(ValidationError):
        SupportAnalysis(**data)


def test_confidence_score_boundaries(support_analysis_data):
    data = support_analysis_data.copy()
    data["confidence_score"] = -0.1
    with pytest.raises(ValidationError):
        SupportAnalysis(**data)

    data["confidence_score"] = 1.1
    with pytest.raises(ValidationError):
        SupportAnalysis(**data)
