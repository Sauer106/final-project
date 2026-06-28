"""Streamlit interface for the AI Help Desk Ticket Assistant.

Architecture:
    user -> Streamlit (app.py) -> db.py (SQL) -> project.db
    Streamlit (app.py) -> ai.py (prompt + model call)

The app displays ticket data, lets the user select a ticket, shows the database
evidence for that ticket, and generates an AI summary from that evidence. The
database is the source of truth; the AI only summarizes evidence shown to the
user.
"""

import streamlit as st

from db import (
    get_all_tickets,
    get_tickets_by_status,
    get_tickets_with_requesters,
    get_ticket_counts_by_status,
    get_ticket_evidence_for_ai,
)
from ai import evidence_dataframe_to_text, generate_ai_response

st.set_page_config(
    page_title="AI Help Desk Ticket Assistant",
    page_icon="\U0001F3AB",
    layout="wide",
)

st.title("AI Help Desk Ticket Assistant")
st.write(
    """
    This application lets a help desk analyst inspect and filter ticket data and
    generate an AI summary of a selected ticket. Every section reads from the
    database through functions in `db.py`, and the AI feature summarizes only the
    database evidence shown on screen.
    """
)

# Everything is wrapped so a database problem shows a clear message instead of a
# blank page or a raw crash.
try:
    # --- Database-backed data display ---
    st.header("All Tickets")
    tickets = get_all_tickets()
    st.dataframe(tickets, use_container_width=True)
    st.caption(f"{len(tickets)} tickets loaded from the database.")

    # --- User-controlled filter (parameterized query) ---
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

    # --- JOIN query result ---
    st.header("Tickets with Requester and Category")
    ticket_context = get_tickets_with_requesters()
    st.dataframe(ticket_context, use_container_width=True)

    # --- Aggregation / GROUP BY result ---
    st.header("Ticket Counts by Status")
    counts = get_ticket_counts_by_status()
    col1, col2 = st.columns(2)
    with col1:
        st.dataframe(counts, use_container_width=True)
    with col2:
        if not counts.empty:
            st.bar_chart(counts.set_index("status"))

    # --- AI Ticket Summary (the database-backed AI feature) ---
    st.header("AI Ticket Summary")
    st.write(
        "Select a ticket to retrieve its evidence from the database and generate "
        "an AI summary. The AI uses only the evidence shown below."
    )
    ticket_id = st.number_input("Enter a ticket ID", min_value=1, step=1, value=1)
    evidence = get_ticket_evidence_for_ai(int(ticket_id))

    st.subheader("Database Evidence Used")
    if evidence.empty:
        # Missing-record handling.
        st.warning("No database evidence found for that ticket ID. Try another ID.")
    else:
        row = evidence.iloc[0]
        st.markdown(f"**#{row['ticket_id']} \u2014 {row['title']}**")
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
        with st.expander("View the raw evidence row sent to the AI"):
            st.dataframe(evidence, use_container_width=True)

        # Convert the database evidence into text for the model.
        evidence_text = evidence_dataframe_to_text(evidence)

        # Required user-facing warning.
        st.warning(
            "AI output is generated from the database evidence shown above. "
            "Always verify the response against the source records \u2014 the "
            "database, not the AI, is the source of truth."
        )

        if st.button("Generate AI Summary"):
            with st.spinner("Generating AI response..."):
                ai_output = generate_ai_response(evidence_text)
            st.subheader("AI-Generated Output")
            st.write(ai_output)
            st.caption(
                "AI-generated from the evidence above. This is an assistant, not "
                "a verified record."
            )

except Exception as error:  # noqa: BLE001
    st.error("The application could not load data from the database.")
    st.write("Make sure the database has been built by running `python seed.py`.")
    st.exception(error)
