"""This module defines intent enums, risk levels, and the
`SupportAnalysis` Pydantic model.
"""
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, model_validator


class PrimaryIntent(str, Enum):
    """Primary high-level customer intent categories."""
    account_access = "account_access"
    account_creation = "account_creation"
    verification = "verification"
    payments_and_funds = "payments_and_funds"
    general_enquiry = "general_enquiry"


class RiskLevel(str, Enum):
    """Risk level categories for support cases."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class SubIntent(str, Enum):
    """Specific sub-intents associated with a `PrimaryIntent`."""
    reset_pin = "reset_pin"
    reset_secure_id = "reset_secure_id"
    sms_not_received = "sms_not_received"
    account_restricted = "account_restricted"
    close_account = "close_account"
    create_new_account = "create_new_account"
    restore_old_account = "restore_old_account"
    address_verification = "address_verification"
    identity_verification = "identity_verification"
    phone_number_verification = "phone_number_verification"
    payment_declined = "payment_declined"
    withdrawal_help = "withdrawal_help"
    NULL = "NULL"


def primary_to_sub_mapping():
    """Helper function to create the mapping of primary intents to their valid sub-intents."""
    return {
        PrimaryIntent.account_access: {
            SubIntent.reset_pin,
            SubIntent.reset_secure_id,
            SubIntent.sms_not_received,
            SubIntent.account_restricted,
            SubIntent.close_account,
        },
        PrimaryIntent.account_creation: {
            SubIntent.create_new_account,
            SubIntent.restore_old_account,
        },
        PrimaryIntent.verification: {
            SubIntent.address_verification,
            SubIntent.identity_verification,
            SubIntent.phone_number_verification,
        },
        PrimaryIntent.payments_and_funds: {
            SubIntent.payment_declined,
            SubIntent.withdrawal_help,
        },
        PrimaryIntent.general_enquiry: {
            SubIntent.NULL,
        },
    }


class SupportAnalysis(BaseModel):
    """Pydantic model representing the analysis of a
    customer support interaction."""
    primary_intent: PrimaryIntent
    primary_sub_intent: Optional[SubIntent]

    secondary_intent: Optional[PrimaryIntent]
    secondary_sub_intent: Optional[SubIntent]

    key_information: List[str]
    risk_level: RiskLevel
    escalation_required: bool
    confidence_score: float = Field(ge=0.0, le=1.0)
    manual_review_required: bool
    suggested_next_steps: List[str]

    @model_validator(mode="after")
    def validate_manual_review(self):
        """Ensure that if confidence is low, manual review is required."""
        if self.confidence_score < 0.6 and not self.manual_review_required:
            raise ValueError(
                "Low confidence score requires manual review to be True")
        return self

    @model_validator(mode="after")
    def validate_escalation(self):
        """Ensure that if risk level is HIGH, escalation is required."""
        if self.risk_level == RiskLevel.HIGH and not self.escalation_required:
            raise ValueError(
                "High risk level requires escalation to be True")
        return self

    @model_validator(mode="after")
    def validate_intent_hierarchy(self):
        """Ensure sub-intents are consistent with their primary intents."""

        if self.primary_sub_intent and self.primary_sub_intent != SubIntent.NULL:
            valid_subs = primary_to_sub_mapping().get(self.primary_intent, set())
            if self.primary_sub_intent not in valid_subs:
                raise ValueError(
                    f"{self.primary_sub_intent} does not belong to {self.primary_intent}"
                )

        if self.secondary_sub_intent and not self.secondary_intent:
            raise ValueError(
                "secondary_sub_intent provided without secondary_intent")

        if self.secondary_intent and self.secondary_sub_intent:
            valid_subs = primary_to_sub_mapping().get(self.secondary_intent, set())
            if self.secondary_sub_intent not in valid_subs:
                raise ValueError(
                    f"{self.secondary_sub_intent} does not belong to {self.secondary_intent}"
                )

        return self
