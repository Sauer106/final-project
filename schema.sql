-- AI Help Desk Ticket Assistant — Schema
-- SQLite schema implementing the Week 2 ERDC Proposal.
-- Enable foreign key enforcement (off by default in SQLite).
PRAGMA foreign_keys = ON;

-- Drop in child-to-parent order so foreign keys never block a drop.
DROP TABLE IF EXISTS ai_summaries;
DROP TABLE IF EXISTS ticket_status_history;
DROP TABLE IF EXISTS ticket_tags;
DROP TABLE IF EXISTS resolutions;
DROP TABLE IF EXISTS ticket_comments;
DROP TABLE IF EXISTS tickets;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS users;

-- People who interact with the system: requesters, analysts, and managers.
CREATE TABLE users (
    user_id   INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL,
    email     TEXT NOT NULL UNIQUE,
    role      TEXT NOT NULL CHECK (role IN ('end_user', 'analyst', 'manager'))
);

-- Lookup table of ticket types used to classify tickets.
CREATE TABLE categories (
    category_id   INTEGER PRIMARY KEY,
    category_name TEXT NOT NULL UNIQUE
);

-- Lookup table of free-form labels that can be applied to tickets.
CREATE TABLE tags (
    tag_id   INTEGER PRIMARY KEY,
    tag_name TEXT NOT NULL UNIQUE
);

-- Central record for each support request.
CREATE TABLE tickets (
    ticket_id   INTEGER PRIMARY KEY,
    user_id     INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    title       TEXT NOT NULL,
    description TEXT NOT NULL,
    priority    TEXT NOT NULL DEFAULT 'Medium'
                CHECK (priority IN ('Low', 'Medium', 'High', 'Critical')),
    status      TEXT NOT NULL DEFAULT 'New'
                CHECK (status IN ('New', 'Open', 'In Progress', 'Resolved', 'Closed')),
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),

    FOREIGN KEY (user_id)     REFERENCES users(user_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

-- Chronological thread of comments on a ticket.
CREATE TABLE ticket_comments (
    comment_id   INTEGER PRIMARY KEY,
    ticket_id    INTEGER NOT NULL,
    user_id      INTEGER NOT NULL,
    comment_text TEXT NOT NULL,
    created_at   TEXT NOT NULL DEFAULT (datetime('now')),

    FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id),
    FOREIGN KEY (user_id)   REFERENCES users(user_id)
);

-- Closing record for a ticket. UNIQUE ticket_id enforces at most one per ticket.
CREATE TABLE resolutions (
    resolution_id   INTEGER PRIMARY KEY,
    ticket_id       INTEGER NOT NULL UNIQUE,
    resolved_by     INTEGER NOT NULL,
    resolution_text TEXT NOT NULL,
    resolved_at     TEXT NOT NULL DEFAULT (datetime('now')),

    FOREIGN KEY (ticket_id)   REFERENCES tickets(ticket_id),
    FOREIGN KEY (resolved_by) REFERENCES users(user_id)
);

-- Junction table resolving the many-to-many relationship between tickets and tags.
CREATE TABLE ticket_tags (
    ticket_id INTEGER NOT NULL,
    tag_id    INTEGER NOT NULL,

    PRIMARY KEY (ticket_id, tag_id),
    FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id),
    FOREIGN KEY (tag_id)    REFERENCES tags(tag_id)
);

-- Audit trail of every status change a ticket undergoes.
CREATE TABLE ticket_status_history (
    history_id INTEGER PRIMARY KEY,
    ticket_id  INTEGER NOT NULL,
    changed_by INTEGER NOT NULL,
    old_status TEXT,
    new_status TEXT NOT NULL
               CHECK (new_status IN ('New', 'Open', 'In Progress', 'Resolved', 'Closed')),
    changed_at TEXT NOT NULL DEFAULT (datetime('now')),

    FOREIGN KEY (ticket_id)  REFERENCES tickets(ticket_id),
    FOREIGN KEY (changed_by) REFERENCES users(user_id)
);

-- Content table storing each AI-generated summary, kept separate from human records.
CREATE TABLE ai_summaries (
    summary_id         INTEGER PRIMARY KEY,
    ticket_id          INTEGER NOT NULL,
    summary_text       TEXT NOT NULL,
    suggested_category TEXT,
    suggested_priority TEXT
                       CHECK (suggested_priority IN ('Low', 'Medium', 'High', 'Critical')),
    model_name         TEXT,
    generated_at       TEXT NOT NULL DEFAULT (datetime('now')),

    FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id)
);
