# Paysafe Customer Support AI Assistant

An AI-powered tool that analyses anonymised customer support enquiries for a financial services company. It classifies intent, assesses risk, and suggests next steps for support agents.

## Architecture

```
Customer Query
      │
      ▼
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  analyse.py  │────▶│   OpenAI API     │────▶│  Raw JSON String│
│  (API call)  │     │  (gpt-5-nano)    │     │                 │
└─────────────┘     └──────────────────┘     └────────┬────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │   validate.py    │
                                              │  - JSON parsing  │
                                              │  - Pydantic model│
                                              │  - Risk overrides│
                                              │  - Confidence adj│
                                              └────────┬────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │  SupportAnalysis │
                                              │   (models.py)    │
                                              └────────┬────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │    app.py        │
                                              │  (Streamlit UI)  │
                                              └─────────────────┘
```

## Features

- **Intent Classification**: Categorises queries into 5 primary intents with 12 possible sub-intents
- **Risk Assessment**: Assigns LOW / MEDIUM / HIGH risk with rule-based overrides for keywords like "fraud", "legal threat", "emergency"
- **Confidence Scoring**: Adjusts model confidence when multiple intents are detected; flags low-confidence results for manual review
- **Escalation Detection**: Automatically flags high-risk cases for escalation
- **Manual review required detection**: Automatically flags complex cases where there is low confidence in the analysis as requiring manual review
- **Suggested Next Steps**: Provides up to 3 actionable steps for the support agent
- **Strict Validation**: Pydantic model validators enforce business rules (e.g., HIGH risk → escalation required)

## Setup

### Prerequisites

- Python 3.10+
- An OpenAI API key

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd paysafe

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```
API_KEY=your-openai-api-key-here
```

## Usage

### Streamlit Web App

```bash
streamlit run app.py
```

This launches a web interface where you can paste a customer message and receive a structured analysis.

### Batch Processing (Jupyter Notebook)

Open `ai_solution.ipynb` in Jupyter or VS Code to run the analysis over a batch of customer queries from an Excel file.

## Running Tests

```bash
pytest
```

Tests cover:
- **`test_models.py`** — Pydantic model validation (valid/invalid intents, risk/escalation rules, confidence boundaries)
- **`test_validate.py`** — JSON parsing, response parsing, risk overrides, confidence adjustment
- **`test_analyse.py`** — API call function with mocked OpenAI client

## Project Structure

| File | Description |
|---|---|
| `models.py` | Pydantic data models and enums for intents, risk levels, and analysis output |
| `analyse.py` | OpenAI API integration for query analysis |
| `validate.py` | JSON validation, Pydantic parsing, risk overrides, and confidence adjustment |
| `app.py` | Streamlit web application |
| `system_prompt.txt` | System prompt defining the classification taxonomy and output schema |
| `ai_solution.ipynb` | Jupyter notebook for prototyping and batch processing |
| `test_*.py` | Pytest test suites |

## Intent Taxonomy

| Primary Intent | Sub-Intents |
|---|---|
| `account_access` | `reset_pin`, `reset_secure_id`, `sms_not_received`, `account_restricted`, `close_account` |
| `account_creation` | `create_new_account`, `restore_old_account` |
| `verification` | `address_verification`, `identity_verification`, `phone_number_verification` |
| `payments_and_funds` | `payment_declined`, `withdrawal_help` |
| `general_enquiry` | _(none)_ |

## Risk Levels

| Level | Description |
|---|---|
| **LOW** | Routine support issue |
| **MEDIUM** | Account blocked/restricted or payment issues |
| **HIGH** | Legal threats, potential fraud, emergency language, complaints |