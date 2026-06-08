"""Streamlit interface for the AI Help Desk Ticket Assistant.

This is the first database-backed version. The AI summarization feature will be
added in a later assignment; for now the app reads and displays ticket records
from the local SQLite database.
"""

import streamlit as st

from db import get_tickets, get_ticket_detail

st.set_page_config(
    page_title="AI Help Desk Ticket Assistant",
    page_icon="\U0001F5C4\uFE0F",
    layout="wide",
)

st.title("AI Help Desk Ticket Assistant")
st.write(
    "This application reads support tickets from a local SQLite database. "
    "The database is the authoritative source of truth for all ticket records."
)

st.subheader("All Tickets")
try:
    tickets = get_tickets()
    st.dataframe(tickets, use_container_width=True)

    st.subheader("Ticket Detail")
    selected = st.selectbox("Select a ticket to inspect", tickets["ticket_id"])
    if selected:
        detail = get_ticket_detail(int(selected))
        st.markdown("**Ticket**")
        st.dataframe(detail["ticket"], use_container_width=True)
        st.markdown("**Comments**")
        st.dataframe(detail["comments"], use_container_width=True)
        st.markdown("**Resolution**")
        if detail["resolution"].empty:
            st.info("This ticket has not been resolved yet.")
        else:
            st.dataframe(detail["resolution"], use_container_width=True)

except Exception as error:  # noqa: BLE001
    st.error("The application could not load database records.")
    st.exception(error)
