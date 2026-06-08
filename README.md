# AI Help Desk Ticket Assistant

A database-backed AI application built with Python, SQL, and Streamlit. This
repository contains the first working version of the project database (schema and
seed data) for the AI Help Desk Ticket Assistant, which helps support analysts
review, classify, and summarize technical support tickets.

## Project Structure

```
final-project/
  README.md
  requirements.txt
  app.py                       Streamlit interface (reads tickets from the database)
  db.py                        Database access functions
  schema.sql                   CREATE TABLE statements and constraints
  seed.py                      Builds data/project.db and loads seed data
  data/
    project.db                 The generated SQLite database
  docs/
    schema_verification.md     Verification queries and their results
    schema_reflection.md       Reflection on the design
    query_portfolio.md         Eight SQL queries with output and explanations
```

## Database Design

The database has nine tables: `users`, `categories`, `tags`, `tickets`,
`ticket_comments`, `resolutions`, `ticket_tags` (a many-to-many junction),
`ticket_status_history` (an audit trail), and `ai_summaries` (stored AI output).
Foreign keys connect them, and `CHECK`, `NOT NULL`, and `UNIQUE` constraints
preserve data quality.

## Build the Database

From inside the `final-project` folder, with your virtual environment active,
build the database and load seed data by running:

```bash
python seed.py
```

The database will be created at:

```
data/project.db
```

Expected output:

```
Database created at: data/project.db
Inserted 71 seed records across 9 tables.
```

Re-running `python seed.py` is safe: it rebuilds the database from scratch each
time. SQLite ships with Python, so no separate database installation is needed.

## Verify the Database

The queries in `docs/schema_verification.md` confirm the record counts and show
sample joins and aggregations. You can also open `data/project.db` in DB Browser
for SQLite or run the queries with the `sqlite3` command line.

## Run the App

Install dependencies and start Streamlit:

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app opens at `http://localhost:8501` and lists tickets read from the
database, with a detail view for each ticket. The AI summarization feature will
be added in a later assignment.
