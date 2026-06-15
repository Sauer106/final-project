"""Database access layer for the AI Help Desk Ticket Assistant.

All SQL lives here so the Streamlit interface (app.py) can stay focused on
presentation. Each function opens a connection, runs one query, and returns a
pandas DataFrame, which Streamlit can display directly.

Architecture:
    Streamlit (app.py) -> database functions (db.py) -> SQL -> data/project.db
"""

import sqlite3
from pathlib import Path

import pandas as pd

# 1. Configuration: where the database lives. A relative path keeps this
#    portable, so it works on any machine that runs from the project root
#    (no hard-coded absolute paths).
DATABASE_PATH = Path("data/project.db")


# 2. Reusable connection function.
def get_connection() -> sqlite3.Connection:
    """Return a connection to the local SQLite database.

    Foreign key enforcement is turned on for every connection because SQLite
    leaves it off by default.

    Expected failure point: if data/project.db does not exist, sqlite3 would
    otherwise create an empty file and every query would fail with
    "no such table". We guard against that with a clear message so the fix
    (running seed.py) is obvious.
    """
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"Database not found at {DATABASE_PATH}. "
            f"Run `python seed.py` to build it first."
        )
    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


# 3. Basic retrieval function — records from one major table.
def get_all_tickets() -> pd.DataFrame:
    """Return every ticket with its core fields, newest first."""
    query = """
        SELECT ticket_id, title, priority, status, created_at
        FROM tickets
        ORDER BY created_at DESC;
    """
    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


# 4. Parameterized query function — uses a caller-supplied value safely.
def get_tickets_by_status(status: str) -> pd.DataFrame:
    """Return tickets matching a given status (e.g., 'Open', 'Resolved').

    The status value is passed as a bound parameter (the `?` placeholder),
    never formatted into the SQL string. This prevents SQL injection and
    handles awkward input safely. An unknown status simply returns no rows.
    """
    query = """
        SELECT ticket_id, title, priority, status
        FROM tickets
        WHERE status = ?
        ORDER BY ticket_id;
    """
    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=(status,))


# 5. JOIN query function — related data from multiple tables.
def get_tickets_with_requesters() -> pd.DataFrame:
    """Return each ticket with its requester name and category name.

    Relies on two foreign keys: tickets.user_id -> users.user_id and
    tickets.category_id -> categories.category_id. This turns raw ID columns
    into human-readable context for the interface.
    """
    query = """
        SELECT t.ticket_id,
               t.title,
               u.full_name     AS requester,
               c.category_name AS category,
               t.priority,
               t.status
        FROM tickets t
        JOIN users u      ON t.user_id = u.user_id
        JOIN categories c ON t.category_id = c.category_id
        ORDER BY t.ticket_id;
    """
    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


# 6. Aggregation / GROUP BY function — summarizes data.
def get_ticket_counts_by_status() -> pd.DataFrame:
    """Return the number of tickets in each status, most common first."""
    query = """
        SELECT status, COUNT(*) AS ticket_count
        FROM tickets
        GROUP BY status
        ORDER BY ticket_count DESC, status;
    """
    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


# 7. AI-support retrieval function — the evidence the future AI feature uses.
def get_ticket_evidence_for_ai(ticket_id: int) -> pd.DataFrame:
    """Return the full evidence bundle for one ticket, for AI summarization.

    Gathers the ticket's structured fields plus its free-text description, the
    concatenated comment thread, and the resolution note (if any) into a single
    row. This is the database-resident evidence that could later be sent to an
    AI model. It does NOT call a model yet.

    Uses a bound parameter for ticket_id. LEFT JOINs are used for comments and
    resolutions so a ticket with neither still returns a row. An invalid
    ticket_id returns an empty DataFrame rather than raising.
    """
    query = """
        SELECT t.ticket_id,
               t.title,
               t.description,
               t.priority,
               t.status,
               c.category_name,
               GROUP_CONCAT(cm.comment_text, ' | ') AS comment_history,
               r.resolution_text
        FROM tickets t
        JOIN categories c            ON t.category_id = c.category_id
        LEFT JOIN ticket_comments cm ON t.ticket_id = cm.ticket_id
        LEFT JOIN resolutions r      ON t.ticket_id = r.ticket_id
        WHERE t.ticket_id = ?
        GROUP BY t.ticket_id, t.title, t.description, t.priority, t.status,
                 c.category_name, r.resolution_text;
    """
    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=(ticket_id,))


# Simple test block so the file can be run directly: `python db.py`
if __name__ == "__main__":
    try:
        print("Testing database access functions...\n")

        print("All tickets (newest first):")
        print(get_all_tickets().to_string(index=False))

        print("\nTickets with status 'Open' (parameterized query):")
        print(get_tickets_by_status("Open").to_string(index=False))

        print("\nTickets with requester and category (JOIN):")
        print(get_tickets_with_requesters().to_string(index=False))

        print("\nTicket counts by status (GROUP BY):")
        print(get_ticket_counts_by_status().to_string(index=False))

        print("\nAI evidence bundle for ticket 10 (AI-support retrieval):")
        evidence = get_ticket_evidence_for_ai(10)
        for col in evidence.columns:
            print(f"  {col}: {evidence.iloc[0][col]}")

    except FileNotFoundError as error:
        print(f"ERROR: {error}")
    except sqlite3.Error as error:
        print(f"DATABASE ERROR: {error}")
