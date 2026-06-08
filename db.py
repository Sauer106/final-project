"""Database access for the AI Help Desk Ticket Assistant.

Keeps SQL and connection handling in one place so the Streamlit interface
(app.py) stays focused on presentation.
"""

import sqlite3
from pathlib import Path

import pandas as pd

DATABASE_PATH = Path("data/project.db")


def get_connection() -> sqlite3.Connection:
    """Return a connection to the local SQLite database with foreign keys enforced."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def get_tickets() -> pd.DataFrame:
    """Return all tickets with their category and submitter for listing in the UI."""
    query = """
        SELECT t.ticket_id,
               t.title,
               c.category_name AS category,
               u.full_name     AS submitted_by,
               t.priority,
               t.status,
               t.created_at
        FROM tickets t
        JOIN categories c ON t.category_id = c.category_id
        JOIN users u      ON t.user_id = u.user_id
        ORDER BY t.ticket_id;
    """
    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


def get_ticket_detail(ticket_id: int) -> dict:
    """Return a single ticket plus its comments and resolution, for the AI feature."""
    with get_connection() as conn:
        ticket = pd.read_sql_query(
            """
            SELECT t.ticket_id, t.title, t.description, t.priority, t.status,
                   c.category_name AS category, u.full_name AS submitted_by
            FROM tickets t
            JOIN categories c ON t.category_id = c.category_id
            JOIN users u      ON t.user_id = u.user_id
            WHERE t.ticket_id = ?;
            """,
            conn, params=(ticket_id,),
        )
        comments = pd.read_sql_query(
            """
            SELECT u.full_name AS author, c.comment_text, c.created_at
            FROM ticket_comments c
            JOIN users u ON c.user_id = u.user_id
            WHERE c.ticket_id = ?
            ORDER BY c.created_at;
            """,
            conn, params=(ticket_id,),
        )
        resolution = pd.read_sql_query(
            "SELECT resolution_text, resolved_at FROM resolutions WHERE ticket_id = ?;",
            conn, params=(ticket_id,),
        )
    return {"ticket": ticket, "comments": comments, "resolution": resolution}
