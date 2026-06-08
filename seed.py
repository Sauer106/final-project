"""Create the AI Help Desk Ticket Assistant database and load seed data.

Run from the project root:

    python seed.py

This builds data/project.db from schema.sql and inserts sample records
that support filtering, joins, and aggregation in later assignments.
"""

import sqlite3
from pathlib import Path

DATABASE_PATH = Path("data/project.db")
SCHEMA_PATH = Path("schema.sql")


USERS = [
    (1, "Maya Chen", "maya.chen@example.com", "end_user"),
    (2, "Jordan Smith", "jordan.smith@example.com", "analyst"),
    (3, "Priya Patel", "priya.patel@example.com", "manager"),
    (4, "Liam O'Brien", "liam.obrien@example.com", "end_user"),
    (5, "Sofia Garcia", "sofia.garcia@example.com", "analyst"),
    (6, "Noah Kim", "noah.kim@example.com", "end_user"),
]

CATEGORIES = [
    (1, "Hardware"),
    (2, "Software"),
    (3, "Network"),
    (4, "Access"),
    (5, "Email"),
]

TAGS = [
    (1, "vpn"),
    (2, "password-reset"),
    (3, "recurring"),
    (4, "hardware-failure"),
    (5, "onboarding"),
    (6, "outage"),
]

# ticket_id, user_id, category_id, title, description, priority, status, created_at
TICKETS = [
    (1, 1, 3, "Cannot connect to VPN",
     "User reports that VPN authentication succeeds but internal resources are unreachable from the home network.",
     "High", "Open", "2026-05-01 09:15:00"),
    (2, 4, 4, "Password reset request",
     "New employee is unable to log in to their workstation and needs an initial password reset and account unlock.",
     "Medium", "Resolved", "2026-05-01 10:40:00"),
    (3, 6, 1, "Laptop will not power on",
     "Laptop shows no signs of power after charging overnight; a battery or charger failure is suspected.",
     "High", "In Progress", "2026-05-02 08:05:00"),
    (4, 1, 2, "Outlook crashes on launch",
     "Outlook closes immediately after opening. The problem began right after the most recent software update.",
     "Medium", "Open", "2026-05-02 13:22:00"),
    (5, 4, 5, "Not receiving external email",
     "User can send and receive internal email but messages from outside the organization never arrive in the inbox.",
     "High", "Resolved", "2026-05-03 11:10:00"),
    (6, 6, 3, "Intermittent Wi-Fi drops",
     "Wi-Fi disconnects every few minutes in the east wing conference rooms, interrupting video calls.",
     "Medium", "In Progress", "2026-05-03 15:45:00"),
    (7, 1, 4, "Access to shared drive denied",
     "User receives a permission denied error when opening the finance shared drive needed for monthly reporting.",
     "Low", "Closed", "2026-05-04 09:30:00"),
    (8, 4, 2, "Software license expired",
     "Design software reports an expired license on startup and will not launch.",
     "Medium", "New", "2026-05-05 14:00:00"),
    (9, 6, 1, "External monitor flickering",
     "External monitor flickers intermittently; swapping the video cable did not resolve the issue.",
     "Low", "Open", "2026-05-05 16:20:00"),
    (10, 1, 3, "Company-wide network outage on third floor",
     "Multiple users report a total loss of network connectivity on the third floor of the main building.",
     "Critical", "Resolved", "2026-05-06 08:00:00"),
]

# comment_id, ticket_id, user_id, comment_text, created_at
TICKET_COMMENTS = [
    (1, 1, 2, "Confirmed the VPN tunnel establishes but routing to the internal subnet fails. Investigating the split-tunnel configuration.", "2026-05-01 09:40:00"),
    (2, 1, 1, "Still cannot reach the file server after reconnecting to the VPN.", "2026-05-01 10:05:00"),
    (3, 2, 5, "Reset the password and unlocked the account. Asked the user to confirm they can log in.", "2026-05-01 11:00:00"),
    (4, 2, 4, "Confirmed I can log in now. Thank you for the quick help.", "2026-05-01 11:15:00"),
    (5, 3, 2, "Ran hardware diagnostics; the battery is not detected. Ordered a replacement battery.", "2026-05-02 09:30:00"),
    (6, 4, 5, "Reproduced the crash on a test machine. Reviewing the recent update logs for the mail add-in.", "2026-05-02 14:00:00"),
    (7, 5, 2, "External mail was being blocked by a misconfigured spam rule. Adjusting the rule now.", "2026-05-03 11:45:00"),
    (8, 6, 5, "Updated the access point firmware in the east wing and am monitoring for further drops.", "2026-05-03 16:30:00"),
    (9, 7, 2, "Added the user to the finance security group; access has been confirmed.", "2026-05-04 10:00:00"),
    (10, 10, 2, "Core switch on the third floor failed over to the backup unit and service was restored.", "2026-05-06 08:35:00"),
    (11, 10, 3, "Please document the root cause for the incident report.", "2026-05-06 09:00:00"),
    (12, 6, 6, "Drops are less frequent today but are still happening occasionally.", "2026-05-04 09:10:00"),
]

# resolution_id, ticket_id, resolved_by, resolution_text, resolved_at
RESOLUTIONS = [
    (1, 2, 5, "Reset the user's password and unlocked the account; the user confirmed a successful login.", "2026-05-01 11:20:00"),
    (2, 5, 2, "Corrected the spam filter rule that was quarantining external mail and verified delivery.", "2026-05-03 12:15:00"),
    (3, 7, 2, "Granted finance shared-drive access through security group membership; the user verified access.", "2026-05-04 10:05:00"),
    (4, 10, 2, "Failed the core switch over to the backup unit, restoring third-floor connectivity.", "2026-05-06 08:40:00"),
]

# ticket_id, tag_id
TICKET_TAGS = [
    (1, 1), (1, 3),
    (2, 2), (2, 5),
    (3, 4),
    (4, 3),
    (5, 3),
    (6, 3),
    (7, 5),
    (8, 3),
    (9, 4),
    (10, 6),
]

# history_id, ticket_id, changed_by, old_status, new_status, changed_at
TICKET_STATUS_HISTORY = [
    (1, 1, 1, None, "New", "2026-05-01 09:15:00"),
    (2, 1, 2, "New", "Open", "2026-05-01 09:35:00"),
    (3, 2, 4, None, "New", "2026-05-01 10:40:00"),
    (4, 2, 5, "New", "Resolved", "2026-05-01 11:20:00"),
    (5, 3, 6, None, "New", "2026-05-02 08:05:00"),
    (6, 3, 2, "New", "In Progress", "2026-05-02 09:30:00"),
    (7, 5, 4, None, "New", "2026-05-03 11:10:00"),
    (8, 5, 2, "New", "Resolved", "2026-05-03 12:15:00"),
    (9, 7, 1, None, "New", "2026-05-04 09:30:00"),
    (10, 7, 2, "New", "Resolved", "2026-05-04 10:05:00"),
    (11, 7, 2, "Resolved", "Closed", "2026-05-04 10:30:00"),
    (12, 10, 1, None, "New", "2026-05-06 08:00:00"),
    (13, 10, 2, "New", "Resolved", "2026-05-06 08:40:00"),
]

# summary_id, ticket_id, summary_text, suggested_category, suggested_priority, model_name, generated_at
AI_SUMMARIES = [
    (1, 1,
     "The user authenticates to the VPN successfully but cannot reach internal resources such as the file server. The analyst suspects a split-tunnel routing issue and is investigating.",
     "Network", "High", "claude-sonnet-4", "2026-05-01 10:10:00"),
    (2, 5,
     "External email was not arriving because of a misconfigured spam rule. The analyst corrected the rule, verified delivery, and resolved the ticket.",
     "Email", "High", "claude-sonnet-4", "2026-05-03 12:20:00"),
    (3, 10,
     "A critical network outage affected multiple users on the third floor. The core switch was failed over to a backup unit, restoring connectivity, and a root-cause report was requested.",
     "Network", "Critical", "claude-sonnet-4", "2026-05-06 09:05:00"),
]


def initialize_database() -> None:
    """Create the project database from schema.sql and insert all seed records."""
    DATABASE_PATH.parent.mkdir(exist_ok=True)

    # Start from a clean file so re-running always produces the same result.
    if DATABASE_PATH.exists():
        DATABASE_PATH.unlink()

    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")

        schema_sql = SCHEMA_PATH.read_text()
        conn.executescript(schema_sql)

        conn.executemany("INSERT INTO users (user_id, full_name, email, role) VALUES (?, ?, ?, ?)", USERS)
        conn.executemany("INSERT INTO categories (category_id, category_name) VALUES (?, ?)", CATEGORIES)
        conn.executemany("INSERT INTO tags (tag_id, tag_name) VALUES (?, ?)", TAGS)
        conn.executemany(
            "INSERT INTO tickets (ticket_id, user_id, category_id, title, description, priority, status, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)", TICKETS)
        conn.executemany(
            "INSERT INTO ticket_comments (comment_id, ticket_id, user_id, comment_text, created_at) "
            "VALUES (?, ?, ?, ?, ?)", TICKET_COMMENTS)
        conn.executemany(
            "INSERT INTO resolutions (resolution_id, ticket_id, resolved_by, resolution_text, resolved_at) "
            "VALUES (?, ?, ?, ?, ?)", RESOLUTIONS)
        conn.executemany("INSERT INTO ticket_tags (ticket_id, tag_id) VALUES (?, ?)", TICKET_TAGS)
        conn.executemany(
            "INSERT INTO ticket_status_history (history_id, ticket_id, changed_by, old_status, new_status, changed_at) "
            "VALUES (?, ?, ?, ?, ?, ?)", TICKET_STATUS_HISTORY)
        conn.executemany(
            "INSERT INTO ai_summaries (summary_id, ticket_id, summary_text, suggested_category, suggested_priority, model_name, generated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)", AI_SUMMARIES)

        conn.commit()

        # Fail loudly if any foreign key is dangling.
        violations = conn.execute("PRAGMA foreign_key_check;").fetchall()
        if violations:
            raise RuntimeError(f"Foreign key violations detected: {violations}")


if __name__ == "__main__":
    initialize_database()
    total = sum(len(t) for t in (
        USERS, CATEGORIES, TAGS, TICKETS, TICKET_COMMENTS,
        RESOLUTIONS, TICKET_TAGS, TICKET_STATUS_HISTORY, AI_SUMMARIES))
    print(f"Database created at: {DATABASE_PATH}")
    print(f"Inserted {total} seed records across 9 tables.")
