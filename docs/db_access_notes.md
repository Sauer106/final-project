# Database Access Notes

## Question 1: Which database access functions did you create, and what does each do?

`db.py` defines a reusable `get_connection()` function plus five access
functions:

- **`get_all_tickets()`** — returns every ticket with its core fields (id,
  title, priority, status, created_at), newest first. This is the basic
  retrieval function for one major table.
- **`get_tickets_by_status(status)`** — returns the tickets that match a given
  status, using a parameterized query.
- **`get_tickets_with_requesters()`** — returns each ticket joined to its
  requester's name and category name.
- **`get_ticket_counts_by_status()`** — returns a count of tickets grouped by
  status (an aggregation / GROUP BY summary).
- **`get_ticket_evidence_for_ai(ticket_id)`** — returns the full evidence
  bundle for one ticket, the data the future AI feature will summarize.

## Question 2: Which function uses a parameterized query? Why is that important?

`get_tickets_by_status(status)` and `get_ticket_evidence_for_ai(ticket_id)` both
use parameterized queries, passing the caller's value through a `?` placeholder
with the `params` argument instead of formatting it into the SQL string. This
matters because it prevents SQL injection: a malicious or malformed value cannot
change the structure of the query. It also handles tricky input (such as text
containing quotes) correctly and keeps the SQL readable.

## Question 3: Which function uses a JOIN? What relationship does it rely on?

`get_tickets_with_requesters()` joins three tables. It relies on two foreign
keys: `tickets.user_id` references `users.user_id`, and `tickets.category_id`
references `categories.category_id`. The join replaces the numeric ID columns
with the requester's name and the readable category name.
`get_ticket_evidence_for_ai()` also joins, adding `LEFT JOIN`s to
`ticket_comments` and `resolutions` so it can include related records that may
or may not exist.

## Question 4: Which function supports your future AI feature? What evidence does it retrieve?

`get_ticket_evidence_for_ai(ticket_id)` supports the planned AI summarization
feature. For one selected ticket it retrieves the structured fields (title,
priority, status, category) plus the free-text description, the full comment
thread concatenated into a single field, and the resolution note if one exists.
That bundle is exactly the database-resident evidence that could later be sent
to an AI model. The function does not call a model yet; it only gathers the
evidence, which keeps the database as the source of truth.

## Question 5: What problems did you encounter while connecting Python to the database?

The main consideration was making the code portable and predictable. I used a
relative path (`data/project.db`) rather than an absolute one so it runs on any
machine from the project root. I also added a guard in `get_connection()` that
raises a clear error if the database file is missing, because SQLite would
otherwise silently create an empty file and every query would fail with "no such
table." The other detail was the AI-support query: joining both comments and
resolutions multiplies rows, so I used `GROUP_CONCAT` with `GROUP BY` to collapse
the comment thread back into one row per ticket.
