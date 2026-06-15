# Streamlit Prototype Notes

## Question 1: What database-backed information does your Streamlit app display?

The app displays ticket data pulled from the project database through `db.py`.
It shows a full table of all tickets, a status-filtered subset, a joined view
of tickets with their requester and category, a count of tickets grouped by
status (with a bar chart), and a detail view for a single selected ticket that
includes its description, comment history, and resolution.

## Question 2: What user-controlled filter or selection did you implement?

Two. A `st.selectbox` lets the user choose a ticket status (New, Open, In
Progress, Resolved, or Closed), which calls the parameterized
`get_tickets_by_status()` function and shows only the matching tickets. A
`st.number_input` lets the user enter a ticket ID to load that ticket's detail
view.

## Question 3: Which JOIN query result is displayed, and why is it useful?

The "Tickets with Requester and Category" section displays the result of
`get_tickets_with_requesters()`, which joins the tickets, users, and categories
tables. It is useful because it replaces raw `user_id` and `category_id` numbers
with the requester's name and the readable category, which is what an analyst
actually needs to see when scanning the queue.

## Question 4: Which aggregation or summary result is displayed?

The "Ticket Counts by Status" section displays `get_ticket_counts_by_status()`,
which uses a SQL GROUP BY to count tickets in each status. The result is shown
both as a table and as a bar chart so the distribution is easy to read at a
glance.

## Question 5: What data does your detail view retrieve?

The detail view calls `get_ticket_evidence_for_ai(ticket_id)`, which returns a
single ticket's full evidence bundle: its title, priority, status, category,
free-text description, the full comment thread concatenated into one field, and
the resolution note if one exists. The app presents these as labeled fields.

## Question 6: Where will the future AI feature be added, and what data will it use?

The "Future AI Feature" section at the bottom holds a placeholder with an
explanatory note and a disabled-style button. That is where the AI summarization
will go. It will use the same evidence the detail view already retrieves through
`get_ticket_evidence_for_ai()` -- the description, comment history, and
resolution -- so the AI only summarizes database-resident records and the
database stays the source of truth.

## Question 7: What is one improvement you plan to make before final submission?

Beyond wiring in the actual AI call, I plan to combine the filters so a user can
narrow by status and priority together, and to display the detail view's comment
history as a formatted timeline rather than one concatenated string, which will
make it easier to read and a cleaner input for the AI summary.
