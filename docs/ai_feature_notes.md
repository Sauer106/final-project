# AI Feature Notes

## What the AI feature does

The AI feature is a **Ticket Summary Assistant**. When an analyst selects a
ticket in the Streamlit app, the feature generates a short, structured summary of
that ticket and suggests a likely issue, a priority, and a next action. It is not
a general-purpose chatbot; it only summarizes the evidence retrieved for the
selected ticket.

## What database data it uses

The feature uses one selected ticket's evidence: the ticket title, description,
priority, status, the category name, the concatenated comment history, and the
resolution text if one exists. This data spans the `tickets`, `categories`,
`ticket_comments`, and `resolutions` tables.

## How the data is retrieved

All retrieval goes through `get_ticket_evidence_for_ai(ticket_id)` in `db.py`,
which runs a single parameterized SQL query. It joins `categories`, LEFT JOINs
`ticket_comments` and `resolutions`, and uses `GROUP_CONCAT` to combine the
comment thread into one field. No SQL is written in `app.py` or `ai.py`.

## What gets sent to the AI model

Only the selected ticket's evidence is sent. In `ai.py`,
`evidence_dataframe_to_text()` converts the retrieved DataFrame into a labeled
text block, and `build_ticket_summary_prompt()` wraps it in an instruction that
tells the model to use only the provided evidence, not to invent facts, and to
respond in a fixed labeled format (Summary, Likely Issue, Suggested Priority,
Recommended Next Action, Missing Information). Nothing else from the database is
sent, and the model cannot modify the database.

## How the output is displayed

The app shows the database evidence first (the ticket's fields, plus an expander
with the raw evidence row), then a warning that the output must be verified, and
only then the AI output under a separate "AI-Generated Output" heading. Keeping
the evidence and the AI response visually separate lets the analyst compare the
summary against the source.

## Why the database remains the source of truth

The AI never writes to the database and never adds facts of its own. It only
rephrases evidence that already exists in the tables and is shown on screen. If
the evidence is thin, the prompt instructs the model to say what is missing
rather than guess. The analyst can always check the AI summary against the
displayed records, so the database, not the model, is authoritative.

## How secrets and configuration are handled

The API key is read from an environment variable (`ANTHROPIC_API_KEY`) loaded
from a local `.env` file via `python-dotenv`. The key is never hardcoded in
`app.py`, `db.py`, or `ai.py`. The `.env` file is listed in `.gitignore` and is
never committed or submitted; a `.env.example` template with a placeholder is
provided instead. If no key is configured, `generate_ai_response()` returns a
clearly labeled mock response so the application still runs end to end.

## Risks and limitations

- **Hallucination.** The model could still introduce a detail not in the
  evidence. Mitigation: the prompt forbids invention, and the evidence is shown
  beside the output for verification.
- **Incomplete records.** A ticket with no comments or resolution yields a
  thinner summary; the prompt asks the model to flag missing information.
- **Over-trust.** A user might accept the summary without checking. Mitigation:
  the app labels the output as AI-generated, shows the source evidence, and warns
  that the summary is not a verified record.
- **Model or key errors.** If the API call fails, the app shows a clear error
  message instead of crashing.
