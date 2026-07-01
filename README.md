# AI Help Desk Ticket Assistant

A database backed AI application built with Python, SQL, and Streamlit. The
AI Help Desk Ticket Assistant helps support analysts review and summarize
technical support tickets, with an AI feature that summarizes a selected ticket
using only database resident evidence.

## Intended Users

Help desk analysts (Tier 1 and Tier 2 support staff) who triage and work support
tickets. Users should be comfortable with a support queue and a web interface but
need no SQL or programming knowledge, since all database access happens behind the
interface. A secondary user is a support lead who wants a quick view of how
tickets are distributed across statuses.

## AI Feature

The AI feature, the Ticket Summary Assistant, summarizes a selected ticket. It
retrieves the ticket's evidence (title, description, priority, status, category,
comment history, and resolution) from the database through
`get_ticket_evidence_for_ai()`, displays that evidence, and sends only that
evidence to the AI helper, which returns a structured summary (summary, likely
issue, suggested priority, recommended next action, missing information). The
source evidence is shown before the AI output so it can be verified, and the AI
never modifies the database.

## Required Software

- Python 3.9 or newer
- The packages listed in `requirements.txt` (`streamlit`, `pandas`,
  `python-dotenv`, `anthropic`), installed with `pip`
- SQLite, which ships with Python, so no separate database installation is needed

## Project Structure

```
final-project/
  README.md
  requirements.txt
  app.py                       Streamlit interface (data display + AI feature)
  db.py                        Database access functions
  ai.py                        AI prompt construction and model call
  schema.sql                   CREATE TABLE statements and constraints
  seed.py                      Builds data/project.db and loads seed data
  .env.example                 Template for the AI API key (copy to .env)
  data/
    project.db                 The generated SQLite database
  docs/
    erd.png                    Entity relationship diagram of the schema
    schema_verification.md     Verification queries and their results
    schema_reflection.md       Reflection on the design
    query_portfolio.md         Eight SQL queries with output and explanations
    db_access_notes.md         Notes on the Python database access layer
    streamlit_prototype_notes.md  Notes on the Streamlit prototype
    ai_feature_notes.md        Notes on the AI integration
    ai_test_report.md          AI feature test plan and results (six test cases)
    risk_failure_analysis.md   Security, risk, and failure analysis
    final_scope_report.md      Final application scope and end state report
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

Rerunning `python seed.py` is safe: it rebuilds the database from scratch each
time. SQLite ships with Python, so no separate database installation is needed.

## Verify the Database

The queries in `docs/schema_verification.md` confirm the record counts and show
sample joins and aggregations. You can also open `data/project.db` in DB Browser
for SQLite or run the queries with the `sqlite3` command line.

## Test Database Access

To rebuild the database:

```bash
python seed.py
```

To test the database access layer in `db.py`:

```bash
python db.py
```

This runs each access function and prints the results to the terminal, which
confirms that Python can connect to the database and retrieve data.

## Run the Streamlit Prototype

1. Rebuild the database (if you have not already):

   ```bash
   python seed.py
   ```

2. Install dependencies and start the app:

   ```bash
   pip install -r requirements.txt
   streamlit run app.py
   ```

3. Open the browser at the local address shown in the terminal (usually
   `http://localhost:8501`).

The prototype displays all tickets, a status filter, a joined view of tickets
with requester and category, ticket counts by status, and an AI ticket summary
feature. All data is read through the functions in `db.py`.

## Run the AI Enabled Prototype

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Rebuild the database:

   ```bash
   python seed.py
   ```

3. Configure AI access. Copy the template and add your key:

   ```bash
   cp .env.example .env
   ```

   Then edit `.env` and set your key:

   ```text
   ANTHROPIC_API_KEY=your_key_here
   ```

   Do not commit or submit your real `.env` file (it is in `.gitignore`). If no
   key is set, the app still runs and the AI feature returns a clearly labeled
   mock response instead of calling a real model.

4. Run the app:

   ```bash
   streamlit run app.py
   ```

### What the AI feature does

In the **AI Ticket Summary** section, select a ticket ID. The app retrieves that
ticket's evidence from the database through `get_ticket_evidence_for_ai()`,
displays the evidence, and (on button click) sends only that evidence to the AI
model via `ai.py`. The model returns a structured summary with a likely issue,
suggested priority, recommended next action, and any missing information. The
database remains the source of truth: the AI summarizes only the displayed
evidence and never modifies any records.

## Mock Mode

This project is configured to run without a paid API key. When no
`ANTHROPIC_API_KEY` is set, `ai.py` returns a clearly labeled placeholder
("[MOCK RESPONSE]") that echoes the retrieved database evidence instead of calling
a live model. This is the mode used for the current submission. To enable a live
model, add a real key to `.env` as shown above; the code path is otherwise
identical and requires no other changes.

## Known Limitations

- **AI output must be verified.** The AI summary must be checked against the
  displayed database evidence. The application does not automatically resolve
  tickets or replace analyst judgment.
- **Mock mode.** The submitted configuration uses a mock AI response, so real
  model behavior (accurate summarization, ambiguity handling, prompt injection
  resistance) is documented but not yet verified. See
  `docs/ai_test_report.md` and `docs/risk_failure_analysis.md`.
- **No access control.** The application has no authentication or role based
  access control; anyone who runs it can view all tickets.
- **Sample data only.** The database uses a small, course safe seed dataset (71
  records) and no live production data.

## API Keys and Security

Do not commit or submit a real API key. The `.env` file is listed in
`.gitignore` and must never be pushed or uploaded. Only the `.env.example`
template (with a placeholder value) is included in the repository. If you enable a
live model, keep your real key in your local `.env` only.
