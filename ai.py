"""AI helper for the AI Help Desk Ticket Assistant.

Keeps prompt construction and the AI model call separate from the database
layer (db.py) and the interface (app.py).

The feature summarizes a single ticket using ONLY the database evidence passed
in. If no API key is configured, it falls back to a clearly labeled mock
response so the application still runs end to end.
"""

import os

from dotenv import load_dotenv

# Load variables from a local .env file (never committed). The API key is read
# from the environment -- it is never hardcoded in source.
load_dotenv()

API_KEY = os.getenv("ANTHROPIC_API_KEY")
AI_MODEL = os.getenv("AI_MODEL", "claude-sonnet-4-20250514")


def evidence_dataframe_to_text(evidence_df) -> str:
    """Convert one ticket's evidence DataFrame into clear text for the model."""
    if evidence_df is None or evidence_df.empty:
        return ""
    row = evidence_df.iloc[0]
    return (
        f"Ticket ID: {row.get('ticket_id')}\n"
        f"Title: {row.get('title')}\n"
        f"Description: {row.get('description')}\n"
        f"Priority: {row.get('priority')}\n"
        f"Status: {row.get('status')}\n"
        f"Category: {row.get('category_name')}\n"
        f"Comment History: {row.get('comment_history')}\n"
        f"Resolution: {row.get('resolution_text')}\n"
    )


def build_ticket_summary_prompt(evidence_text: str) -> str:
    """Build the instruction sent to the AI model."""
    return f"""You are assisting a help desk analyst.

Use only the database evidence provided below. Do not invent facts, users,
ticket history, or resolution steps. If information is missing, say what is
missing rather than guessing.

Produce output in exactly this format:

Summary:
Likely Issue:
Suggested Priority:
Recommended Next Action:
Missing Information:

Database Evidence:
{evidence_text}
"""


def _mock_response(evidence_text: str) -> str:
    """Fallback used only when no API key is configured."""
    return (
        "Summary:\n"
        "[MOCK RESPONSE] No AI API key is configured, so this is a placeholder "
        "generated locally from the database evidence rather than by a real "
        "model.\n\n"
        "Key Evidence Observed:\n"
        f"{evidence_text[:750]}\n\n"
        "Missing Information:\n"
        "To produce a real AI summary, set ANTHROPIC_API_KEY in a .env file."
    )


def generate_ai_response(evidence_text: str) -> str:
    """Send the evidence to the AI model and return its structured summary.

    Returns a clear message instead of raising if the evidence is empty, no key
    is configured, or the API call fails.
    """
    if not evidence_text:
        return "No database evidence was provided, so there is nothing to summarize."

    # No key configured -> safe, clearly labeled fallback so the app still runs.
    if not API_KEY:
        return _mock_response(evidence_text)

    prompt = build_ticket_summary_prompt(evidence_text)
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=API_KEY)
        message = client.messages.create(
            model=AI_MODEL,
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text
    except Exception as error:  # noqa: BLE001
        return (
            "The AI request could not be completed, so no summary was generated.\n"
            f"Error: {error}\n\n"
            "Check that your API key and model name are valid, then try again."
        )
