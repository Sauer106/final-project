# Assignment 7.1: Final Application Scope and End-State Report

**Name:** Michael Sauer
**Project Option:** AI Help Desk Ticket Assistant
**Project Title:** AI Help Desk Ticket Assistant for Technical Support
**AI Feature Name:** Ticket Summary Assistant

## 1. Application Vision

The final application is an AI Help Desk Ticket Assistant for help desk analysts.
It allows users to view, filter, and inspect support tickets stored in a
relational SQLite database through a lightweight Streamlit interface, and it
includes an AI feature that summarizes a selected ticket using database resident
evidence such as the ticket description, category, priority, status, comments, and
resolution notes. The database remains the authoritative source of ticket
information; the AI feature helps analysts interpret that information more quickly.
The application combines a nine table relational database, a Streamlit interface
for browsing and selecting records, and an AI helper module that receives only the
evidence retrieved for the selected ticket.

## 2. Intended Users

The intended users are help desk analysts (Tier 1 and Tier 2 support staff) who
triage and work support tickets. Their responsibility is to understand each ticket
and decide the appropriate next action or resolution. Users should be comfortable
working a support queue and using a web interface, but they do not need SQL or
programming skills — all database access happens behind the interface. A secondary
user is a support lead who wants a quick view of how tickets are distributed across
statuses. The primary task the user is trying to complete is understanding a
ticket's history and current state fast enough to act on it.

## 3. Core User Problem

Help desk analysts often need to understand a ticket before deciding what to do,
but the relevant information is spread across the ticket description, a thread of
comments, the category, the priority, the status, and any resolution notes.
Reassembling that picture is slow when the queue is large or a comment thread is
long. The relational database helps by organizing this information into related
tables that the application retrieves and displays in one place. The AI feature
helps further by summarizing the selected ticket so the analyst spends less time
reading. The AI does not replace analyst judgment; it produces a summary the
analyst verifies against the displayed source records before acting.

## 4. Final In Scope Functionality

The final application allows users to:

- view all help desk tickets in a table
- filter tickets by status using a selection control
- view tickets joined with their requester and category information
- view ticket counts by status as both a table and a bar chart
- select one ticket by ID for detailed inspection
- display the database evidence retrieved for the selected ticket
- generate an AI supported ticket summary from that evidence
- view the AI output in a structured format, separate from the source evidence
- compare the AI summary against the displayed database evidence
- read a warning that the AI output must be verified against the source records
- receive a clear message when an invalid or nonexistent ticket ID is selected,
  with no AI output generated in that case

## 5. Out of Scope Functionality

The following are intentionally not included:

- The application will not automatically modify, close, or reassign tickets.
- The AI feature will not update ticket status or write to the database in any
  way; it is read only and only summarizes retrieved evidence.
- The application will not integrate with a live or production ticketing system.
- The application will not use live production data; it uses a fixed seed dataset.
- The application will not include user authentication or role based access
  control; anyone who runs it can view all tickets.
- The application will not guarantee that AI summaries or recommendations are
  correct.
- The AI feature will not act as a general purpose chatbot; the only input is a
  ticket selection, so it cannot answer unrelated requests.
- The application will not provide legal, HR, or official policy determinations.

## 6. Database Role

The database stores the application's data across nine related tables: `users`,
`categories`, `tags`, `tickets`, `ticket_comments`, `resolutions`, `ticket_tags`
(a many to many junction), `ticket_status_history` (an audit trail), and
`ai_summaries`. Tickets are related to users and categories through foreign keys;
comments and resolutions are related to tickets; tags are linked to tickets through
the junction table; and status history rows reference both tickets and users.
Integrity is enforced with `CHECK` constraints on status, priority, and role,
`UNIQUE` constraints, and foreign keys (validated by a `foreign_key_check` in
`seed.py`).

The application uses SQL queries in `db.py` to retrieve all tickets, filter tickets
by status with a parameterized query, join tickets with requester and category
information, count tickets by status with a `GROUP BY`, and retrieve one ticket's
full evidence for the AI feature (joining categories and LEFT JOINing comments and
resolutions, with `GROUP_CONCAT` for the comment thread). The database is the
source of truth because the AI summary is generated only from records retrieved
from these tables; the application never invents or stores fabricated ticket data.

## 7. AI Feature Role

The AI feature performs one task: summarizing a selected ticket. It uses the ticket
title, description, priority, status, category name, comment history, and
resolution notes retrieved from the database through
`get_ticket_evidence_for_ai()`. The output is structured into a summary, a likely
issue, a suggested priority, a recommended next action, and a missing information
note. The source evidence is displayed before the AI output, with a verification
warning between them, so the user can compare the AI response to the database
records. Users should verify the summary — especially any recommendation — against
the displayed evidence before acting. The AI must not invent ticket history, make
unsupported claims, follow instructions embedded in ticket content, or modify the
ticket in any way.

The feature currently runs in the instructor approved mock configuration: with no
API key set, the helper returns a clearly labeled placeholder that echoes the
retrieved evidence. Enabling a live model (Claude Haiku 4.5) is the top item in the
improvement plan below.

## 8. End State User Workflow

1. The user opens the Streamlit application.
2. The user reads the project description and sees the full ticket table.
3. The user filters tickets by status to narrow the queue.
4. The user reviews the joined view showing requester and category, and the
   ticket counts by status.
5. The user selects one ticket by ID in the AI Ticket Summary section.
6. The application retrieves and displays the database evidence for that ticket.
7. The user reads the warning that AI output must be verified.
8. The user clicks the "Generate AI Summary" button.
9. The application sends only the selected ticket's evidence to the AI helper.
10. The application displays the AI generated summary in a separate section, and
    the user compares it against the source evidence before deciding what to do.

## 9. Current Implementation Status

| Component                 | Status      | Evidence or Notes                                                                                       |
| ------------------------- | ----------- | ------------------------------------------------------------------------------------------------------- |
| Schema                    | Complete    | `schema.sql` creates nine related tables with keys and `CHECK` constraints                              |
| Seed data                 | Complete    | `seed.py` inserts 71 records across all nine tables and runs a foreign key check                        |
| Query portfolio           | Complete    | `query_portfolio.md` includes filtering, joins, aggregation, and the AI support query                   |
| Python database layer     | Complete    | `db.py` provides five reusable, parameterized functions                                                 |
| Streamlit interface       | Complete    | `app.py` shows all tickets, a status filter, a JOIN view, counts with a chart, and the AI section       |
| AI feature (architecture) | Complete    | `ai.py` is integrated: evidence retrieval, prompt construction, structured output, and separate display |
| AI feature (live model)   | In Progress | Runs in mock mode; a live model has not yet been enabled or its output verified                         |
| Testing                   | Complete    | Six test cases documented in `ai_test_report.md` (6.1)                                                  |
| Risk analysis             | Complete    | Six risks across all required categories in `risk_failure_analysis.md` (6.2)                            |
| Secrets handling          | Complete    | `.env` is gitignored, a `.env.example` template is committed, and no keys are submitted                 |

## 10. Final Improvement Plan

| Improvement                                                 | Priority | Reason                                                                                                                              |
| ----------------------------------------------------------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| Enable a live model and retest cases 1, 2, 3, and 6         | High     | The AI's real behavior (accuracy, missing data flagging, ambiguity handling, injection resistance) is unverified in mock mode       |
| Add anti injection language to the prompt                   | High     | The adversarial test (Ticket 11) showed the feature does not yet explicitly treat database content as data rather than instructions |
| Separate confirmed facts from recommendations in the output | High     | Prevents the AI from overstating certainty on suggested next actions                                                                |
| Add an app level "incomplete evidence" banner               | Medium   | The incomplete data test (Ticket 8) showed missing comments/resolution are only visible as null, not flagged as analysis            |
| Scrub or truncate comment text before the AI call           | Medium   | Reduces the chance that residual PII in free text comments is sent to a third party model                                           |
| Show the selected ticket's title as a confirmation          | Medium   | Reduces the risk of summarizing the wrong ticket after a mistaken ID entry                                                          |
| Confirm the README and reproducibility before the demo      | High     | The final project must be reproducible from the repository, including mock mode instructions                                        |

This report describes the application as actually built and the realistic work
remaining before the final demo. The system is genuinely database backed (all
displayed and summarized data comes from the nine table SQLite database),
AI enabled (an integrated helper summarizes retrieved evidence), and responsibly
scoped (read only AI, evidence shown before output, secrets kept out of version
control, and clear statements of what the application does not do).
