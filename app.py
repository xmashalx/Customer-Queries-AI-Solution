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
    st.title("Customer Support Interaction Analysis")

    st.subheader("Enter an excel file containing customer support queries:")
    uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx"])

    if uploaded_file is not None:
        queries_df = pd.read_excel(uploaded_file)
        st.write("Queries loaded:")

        # Assuming the Excel file has a column named 'TEXT' containing the queries
        if 'TEXT' not in queries_df.columns:
            st.error(
                "The uploaded Excel file must contain a 'TEXT' column with the queries.")
            return

        # allow user to select a query by id assuming there is an ID column in the loaded dataframe
        if 'ID' not in queries_df.columns:
            st.error(
                "The uploaded Excel file must contain an 'ID' column with the query IDs.")
            return
        else:
            query_id = st.selectbox("Select a query ID", queries_df['ID'])

            if query_id is not None:
                query_text = queries_df.loc[queries_df['ID']
                                            == query_id, 'TEXT'].values[0]
                st.write(f"Selected Query: {query_text}")

                if st.button("Run Analysis"):
                    with st.spinner("Analyzing..."):
                        analysis_result = run_analysis(query_text)
                    st.success("Analysis complete!")

                    # Display the analysis result in a structured format
                    # if the requires manual review is true, show a warning and request that a human review the result
                    # if the requires escalation is true, show a warning and recommend escalation to a supervisor
                    # display in a box the primary intent colon sub intent and in a box next to it the key information
                    # do the same for the secondary intent and sub intent if they exist
                    # display the next steps as a list of actions to take
                    st.subheader("Analysis Result:")
                    if analysis_result.manual_review_required:
                        st.warning(
                            "Low confidence score - manual review required")
                    if analysis_result.escalation_required:
                        st.warning("High risk level - escalation recommended")
                    st.write(
                        f"Primary Intent: {analysis_result.primary_intent} - {analysis_result.primary_sub_intent}")
                    st.write(
                        f"Key Information: {', '.join(analysis_result.key_information)}")
                    if analysis_result.secondary_intent:
                        st.write(
                            f"Secondary Intent: {analysis_result.secondary_intent} - {analysis_result.secondary_sub_intent}")
                    st.write("Suggested Next Steps:")
                    for step in analysis_result.suggested_next_steps:
                        st.write(f"- {step}")


if __name__ == "__main__":
    main()
