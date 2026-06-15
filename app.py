"""Streamlit interface for the AI Help Desk Ticket Assistant.

This is the first working prototype. It reads everything through the functions
in db.py -- no SQL lives in this file -- and displays ticket data, a status
filter, a JOIN result, an aggregation, a detail view, and a placeholder for the
future AI feature. No AI model is called yet.

Run with:
    streamlit run app.py
"""

import streamlit as st

from db import (
    get_all_tickets,
    get_tickets_by_status,
    get_tickets_with_requesters,
    get_ticket_counts_by_status,
    get_ticket_evidence_for_ai,
)

# 1. Clear title and short description.
st.set_page_config(
    page_title="AI Help Desk Ticket Assistant",
    page_icon="\U0001F3AB",
    layout="wide",
)

st.title("AI Help Desk Ticket Assistant")
st.write(
    """
    This prototype lets a help desk analyst inspect, filter, and review the
    ticket data stored in a relational database. Every section below reads from
    the database through functions in `db.py`. A later version will use the
    ticket evidence shown here to generate AI-supported summaries.
    """
)

# 9. Everything is wrapped so a database problem shows a clear message instead
#    of a blank page or a raw crash.
try:
    # 2 + 8. Database-backed data display (calls db.py).
    st.header("All Tickets")
    tickets = get_all_tickets()
    st.dataframe(tickets, use_container_width=True)
    st.caption(f"{len(tickets)} tickets loaded from the database.")

    # 3. User-controlled filter, backed by a parameterized query.
    st.header("Filter Tickets by Status")
    status = st.selectbox(
        "Choose a ticket status",
        ["New", "Open", "In Progress", "Resolved", "Closed"],
    )
    filtered = get_tickets_by_status(status)
    if filtered.empty:
        st.info(f"No tickets currently have the status '{status}'.")
    else:
        st.dataframe(filtered, use_container_width=True)

    # 4. JOIN query result.
    st.header("Tickets with Requester and Category")
    st.write(
        "This view joins the tickets, users, and categories tables so each "
        "ticket shows who submitted it and what type of issue it is."
    )
    ticket_context = get_tickets_with_requesters()
    st.dataframe(ticket_context, use_container_width=True)

    # 5. Aggregation / GROUP BY result, with a chart.
    st.header("Ticket Counts by Status")
    counts = get_ticket_counts_by_status()
    col1, col2 = st.columns(2)
    with col1:
        st.dataframe(counts, use_container_width=True)
    with col2:
        if not counts.empty:
            st.bar_chart(counts.set_index("status"))

    # 6. Detail view -- reuses the AI-support retrieval function.
    st.header("Ticket Detail / AI Evidence Preview")
    st.write(
        "Select a ticket to see the full evidence bundle that the future AI "
        "feature would summarize."
    )
    ticket_id = st.number_input("Enter a ticket ID", min_value=1, step=1, value=1)
    evidence = get_ticket_evidence_for_ai(int(ticket_id))

    if evidence.empty:
        st.warning("No ticket found for that ID.")
    else:
        row = evidence.iloc[0]
        st.subheader(f"#{row['ticket_id']} - {row['title']}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Priority", row["priority"])
        c2.metric("Status", row["status"])
        c3.metric("Category", row["category_name"])
        st.markdown("**Description**")
        st.write(row["description"])
        st.markdown("**Comment history**")
        st.write(row["comment_history"] if row["comment_history"] else "No comments yet.")
        st.markdown("**Resolution**")
        st.write(row["resolution_text"] if row["resolution_text"] else "Not resolved yet.")

    # 7. Future AI feature placeholder.
    st.header("Future AI Feature")
    st.info(
        """
        In the next phase, this section will take the selected ticket's evidence
        -- its description, comment history, and resolution -- and use an AI model
        to generate a short summary and a suggested category or next step. The
        database will remain the source of truth; the AI will only summarize what
        is shown above.
        """
    )
    if st.button("Generate AI Summary (placeholder)"):
        st.warning(
            "AI integration has not been implemented yet -- it is coming in a "
            "later assignment."
        )

except Exception as error:  # noqa: BLE001
    st.error("The Streamlit prototype could not load data from the database.")
    st.write("Make sure the database has been built by running `python seed.py`.")
    st.exception(error)
