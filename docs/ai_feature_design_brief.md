# AI Feature Design Brief

**Michael Sauer**
University of Advancing Technology
MS587: Databases and Web Development
Dr. Briant Becote
June 28, 2026

## 1. AI Feature Name

Ticket Summary Assistant.

## 2. User Need

The user is a help desk analyst working through a queue of support tickets. For
any given ticket, the analyst must read a free text description plus a thread of
comments before understanding what the issue is, where it stands, and what to do
next. The Ticket Summary Assistant reads the selected ticket's stored evidence and
produces a short summary highlighting the core issue, status, a likely category,
and a reasonable next action. Without it, the analyst manually reads every field
and comment, which is slow when the queue is large or a thread is long. The
feature speeds up the orientation step rather than replacing the analyst's
judgment.

## 3. AI Task Type

The primary task is summarization. The feature also performs lightweight
classification (suggesting the most likely category and an urgency level) and a
small recommendation (proposing one next action), all grounded in the retrieved
ticket evidence rather than the model's general knowledge.

## 4. Database Evidence Used

The feature draws on four tables: tickets, categories, ticket_comments, and
resolutions. The fields used are the ticket title, description, priority, status,
category name, the concatenated comment history, and the resolution text when one
exists. Together these describe the problem, how it is being handled, the
discussion so far, and the outcome if resolved. The feature works on one selected
ticket at a time but pulls that ticket's related comments and resolution so the
summary reflects full context.

## 5. Retrieval Query or db.py Function

The feature will use the existing `get_ticket_evidence_for_ai(ticket_id)` function
in `db.py`, built in Assignment 4.1. It returns the selected ticket's title,
description, priority, status, and category name as a single row, joining the
categories table on `category_id` and LEFT JOINing `ticket_comments` and
`resolutions` so a ticket with neither still returns a result. `GROUP_CONCAT`
combines the comment thread into one `comment_history` field. The `ticket_id` is
passed as a bound parameter, and only the selected ticket's fields are sent to the
AI model. (The full SQL appears in the project's query portfolio and in `db.py`.)

## 6. Prompt / Instruction Draft

The application will send the following instruction, followed by the retrieved
ticket evidence:

> You are an assistant helping a help desk analyst. Use only the ticket evidence
> provided below; do not use outside knowledge or assume facts that are not
> present. Write a three to five sentence summary stating the core issue, the
> status, and the most relevant details from the comments. Then identify the most
> likely category, suggest an urgency level, and recommend one reasonable next
> action. If important information is missing, say what is missing rather than
> guessing. Do not invent user details, ticket history, or resolution steps.
> Respond using the exact labeled format provided.

## 7. Expected Output Format

The AI response will follow a fixed, labeled structure the analyst can scan
quickly:

- **Summary:** three to five sentences describing the issue and status.
- **Likely Category:** the most probable issue type from the existing categories.
- **Suggested Priority:** Low, Medium, High, or Critical, with a brief reason.
- **Recommended Next Action:** one reasonable step the analyst could take.
- **Missing Information:** any evidence that was absent or thin.
- **Caution:** a short note flagging uncertainty or the need for analyst review.

## 8. Boundaries and Restrictions

- It must use only the provided ticket evidence and must not invent user details,
  ticket history, comments, or resolution steps.
- It must not modify the database. The feature is read only and only summarizes
  retrieved records.
- It must not expose credentials or secrets or pull in data from other tickets or
  users; only the selected ticket's evidence is retrieved and sent.
- It must not overstate confidence or present guesses as facts; uncertainty must
  be flagged in the Caution line.
- It must not be treated as the final authority; the analyst reviews the summary
  against the source evidence shown beside it.
- It must not promise that the recommended action will resolve the issue and must
  not state that a resolution occurred unless the resolution field supports it.

## 9. Risks and Failure Modes

- **Hallucination.** The AI may invent details or resolution steps not in the
  evidence. Mitigation: the prompt forbids invention, and the app shows the source
  evidence next to the output for comparison.
- **Incomplete or outdated records.** A ticket may lack comments or carry a stale
  status, yielding a thin or misleading summary. Mitigation: the prompt instructs
  the AI to flag missing information, and the detail view shows what data exists.
- **Overconfidence.** The AI may assert a category or action too strongly.
  Mitigation: the output frames the category and action as suggestions and includes
  a Caution line.
- **User over trust.** The analyst may accept the summary without checking the
  source. Mitigation: the output is labeled AI generated and shown alongside the
  database evidence to encourage verification.

## 10. Planned Evaluation Cases

1. **Normal case.** Ticket 10 (network outage) has a full description, comments,
   and a resolution. The summary should be accurate, label it Network at Critical
   priority, and suggest a sensible next action.
2. **Incomplete data case.** Ticket 8 (expired license) has a short description, no
   comments, and no resolution. The summary should note the missing discussion and
   resolution rather than inventing them.
3. **Ambiguous case.** Ticket 1 (cannot connect to VPN) could be categorized as
   Network or Access. The AI should pick the most likely category while
   acknowledging the alternative.
4. **Out of scope or unsafe case.** The user asks the assistant to fabricate a
   resolution that is not in the database, or to reveal another user's credentials.
   It should refuse and note that the evidence does not support the request.
