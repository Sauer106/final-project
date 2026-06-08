# Schema Reflection

## 1. What changes, if any, did you make from your ERDC Proposal?

The schema implements the ERDC Proposal essentially as designed, with all nine
entities and the same relationships. The only refinements were ones the proposal
itself flagged as open questions. I committed to enforcing `priority` and
`status` with `CHECK` constraints rather than separate lookup tables, since that
is simpler for this first build. I also added `DEFAULT` values (status defaults
to `New`, priority to `Medium`, and the timestamp fields to the current time) and
left `ticket_status_history.old_status` nullable so the first row in a ticket's
history can represent its creation.

## 2. Which constraints did you include, and why?

Every table has a primary key so each row is uniquely identifiable. Foreign keys
connect tickets to their submitter and category, comments and history to their
ticket and author, resolutions to their ticket and resolver, and the junction and
summary tables to their parents — this preserves referential integrity.
`NOT NULL` protects the fields the application cannot function without, including
the ticket title and description, comment text, and resolution text. `UNIQUE`
prevents duplicates on `users.email`, `categories.category_name`, and
`tags.tag_name`, and on `resolutions.ticket_id` it enforces the one-resolution-
per-ticket rule. `CHECK` constraints restrict `role`, `priority`, `status`, and
`new_status` to a controlled vocabulary so invalid values cannot be stored.

## 3. How does your seed data support future SQL queries?

The seed data deliberately spreads tickets across every status and priority level
and across all five categories, so queries that filter or group by those fields
return meaningful distributions. Some tickets have multiple comments while others
have none, which supports join-and-aggregate queries and `LEFT JOIN` queries that
distinguish resolved from unresolved tickets. The `ticket_tags` rows exercise the
many-to-many relationship, and the status-history rows provide the data needed to
reconstruct a ticket's timeline.

## 4. Which table or field will be most important for your planned AI feature?

The free-text fields are the heart of the AI feature: `tickets.description`,
`ticket_comments.comment_text`, and `resolutions.resolution_text`. These hold the
narrative the model summarizes, so their quality directly shapes summary quality.
The `ai_summaries` table is also central, since it stores the generated output
alongside its source ticket, keeping AI content separate from the human-entered
records that serve as the source of truth.

## 5. What part of your schema may need revision later?

Three areas may change. First, `priority` and `status` could move into lookup
tables if the application needs to manage those labels dynamically or attach
metadata such as service-level targets. Second, I have not decided whether
`ticket_status_history` should be populated by application code or by a database
trigger that guarantees no change is missed. Third, in `ai_summaries` I may
revisit whether to keep every generated summary or only the latest, and whether
`suggested_category` should become a foreign key to `categories` rather than free
text.
