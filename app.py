"""Streamlit app for analyzing customer support interactions using the SupportAnalysis model."""


import os
from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd
from models import SupportAnalysis, PrimaryIntent, SubIntent
from analyse import analyse_query
from validate import valid_json, parse_response, apply_risk_overrides, adjust_confidence
import streamlit as st


def run_analysis(query: str) -> SupportAnalysis:
    """Run the full analysis pipeline on the given query."""

    load_dotenv()
    client = OpenAI(api_key=os.getenv("API_KEY"))

    raw_response = analyse_query(query, client)

    analysis_dict = valid_json(raw_response)
    analysis = parse_response(analysis_dict)

    analysis = apply_risk_overrides(query, analysis)
    analysis = adjust_confidence(analysis)

    return analysis


def main():
    st.set_page_config(
        page_title="Paysafe Support Assistant", layout="centered")

    st.title("Paysafe Support Assistant")

    st.markdown("Enter a customer message below to analyse.")

    user_input = st.text_area(
        "Customer Message",
        height=150,
        placeholder="Paste or type the customer query here..."
    )

    if st.button("Analyse"):

        if not user_input.strip():
            st.warning("Please enter a customer message.")
            return

        with st.spinner("Analysing message..."):
            try:
                analysis = run_analysis(user_input)
            except Exception as e:
                st.error(f"Analysis failed: {e}")
                return

        st.divider()

        # --- Compact Classification ---
        st.subheader("Classification")

        with st.container(border=True):
            st.markdown(f"### {analysis.primary_intent.value}")
            st.markdown(f"**Sub-Intent:** {analysis.primary_sub_intent.value}")

            if analysis.secondary_intent:
                st.markdown("---")
                st.markdown(f"Secondary: {analysis.secondary_intent.value}")
                st.markdown(f"Sub: {analysis.secondary_sub_intent.value}")

        # --- Expandable Details ---
        with st.expander("Key Information"):
            for item in analysis.key_information:
                st.write(f"• {item}")

        with st.expander("Suggested Next Steps"):
            for step in analysis.suggested_next_steps:
                st.write(f"• {step}")

        with st.expander("Risk & Confidence"):
            st.progress(float(analysis.confidence_score))

            if analysis.manual_review_required:
                st.warning("Manual review required")

            if analysis.escalation_required:
                st.error("Escalation recommended")


if __name__ == "__main__":
    main()
