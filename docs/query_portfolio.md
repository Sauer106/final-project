# Query Portfolio — AI Help Desk Ticket Assistant

This portfolio contains eight SQL queries run against `data/project.db`, the
database created in Assignment 3.1. Every output below is the real result of
running the query against the seeded database. The queries progress from simple
inspection to the kind of evidence retrieval the AI summarization feature will
depend on.

---

## Query 1: Basic SELECT

### Purpose
Confirm that ticket records exist and show the core fields an analyst scans
first: title, status, and priority.

### SQL
```sql
SELECT ticket_id, title, status, priority
FROM tickets;
```

### Output
| ticket_id | title | status | priority |
| --- | --- | --- | --- |
| 1 | Cannot connect to VPN | Open | High |
| 2 | Password reset request | Resolved | Medium |
| 3 | Laptop will not power on | In Progress | High |
| 4 | Outlook crashes on launch | Open | Medium |
| 5 | Not receiving external email | Resolved | High |
| 6 | Intermittent Wi-Fi drops | In Progress | Medium |
| 7 | Access to shared drive denied | Closed | Low |
| 8 | Software license expired | New | Medium |
| 9 | External monitor flickering | Open | Low |
| 10 | Company-wide network outage on third floor | Resolved | Critical |

### Explanation
The tickets table holds ten records spanning every status and priority value.
This is the base list the Streamlit interface will render before an analyst
drills into any single ticket.

---

## Query 2: Filtered WHERE

### Purpose
Retrieve only the tickets that need attention first — those at High or Critical
priority — to show that a specific subset can be isolated.

### SQL
```sql
SELECT ticket_id, title, priority, status
FROM tickets
WHERE priority IN ('High', 'Critical');
```

### Output
| ticket_id | title | priority | status |
| --- | --- | --- | --- |
| 1 | Cannot connect to VPN | High | Open |
| 3 | Laptop will not power on | High | In Progress |
| 5 | Not receiving external email | High | Resolved |
| 10 | Company-wide network outage on third floor | Critical | Resolved |

### Explanation
Four of the ten tickets are High or Critical priority. A filter like this powers
a "needs attention" view in the application, letting analysts focus on the most
urgent work rather than scrolling the full queue.

---

## Query 3: ORDER BY / LIMIT

### Purpose
Show the five most recently created tickets, demonstrating control over result
ordering and size.

### SQL
```sql
SELECT ticket_id, title, created_at
FROM tickets
ORDER BY created_at DESC
LIMIT 5;
```

### Output
| ticket_id | title | created_at |
| --- | --- | --- |
| 10 | Company-wide network outage on third floor | 2026-05-06 08:00:00 |
| 9 | External monitor flickering | 2026-05-05 16:20:00 |
| 8 | Software license expired | 2026-05-05 14:00:00 |
| 7 | Access to shared drive denied | 2026-05-04 09:30:00 |
| 6 | Intermittent Wi-Fi drops | 2026-05-03 15:45:00 |

### Explanation
Sorting by `created_at DESC` with a `LIMIT` produces a "most recent tickets"
feed. This is the pattern behind dashboard widgets that surface the newest
activity without loading every record.

---

## Query 4: JOIN #1 — Tickets with Requester and Category

### Purpose
Combine tickets with their submitter and category so records read in human terms
rather than as raw foreign-key IDs. This demonstrates that the foreign key
relationships work.

### SQL
```sql
SELECT t.ticket_id, t.title, u.full_name AS requester_name,
       c.category_name, t.priority, t.status
FROM tickets t
JOIN users u      ON t.user_id = u.user_id
JOIN categories c ON t.category_id = c.category_id
ORDER BY t.ticket_id;
```

### Output
| ticket_id | title | requester_name | category_name | priority | status |
| --- | --- | --- | --- | --- | --- |
| 1 | Cannot connect to VPN | Maya Chen | Network | High | Open |
| 2 | Password reset request | Liam O'Brien | Access | Medium | Resolved |
| 3 | Laptop will not power on | Noah Kim | Hardware | High | In Progress |
| 4 | Outlook crashes on launch | Maya Chen | Software | Medium | Open |
| 5 | Not receiving external email | Liam O'Brien | Email | High | Resolved |
| 6 | Intermittent Wi-Fi drops | Noah Kim | Network | Medium | In Progress |
| 7 | Access to shared drive denied | Maya Chen | Access | Low | Closed |
| 8 | Software license expired | Liam O'Brien | Software | Medium | New |
| 9 | External monitor flickering | Noah Kim | Hardware | Low | Open |
| 10 | Company-wide network outage on third floor | Maya Chen | Network | Critical | Resolved |

### Explanation
The three-table join replaces `user_id` and `category_id` with the requester's
name and the readable category. The Streamlit interface needs this context so
analysts see who reported an issue and what type it is, and the AI feature uses
the category name when summarizing or classifying a ticket.

---

## Query 5: JOIN #2 — Comment History with Author and Ticket

### Purpose
Answer a different question from Query 4: who said what, and when, across the
comment thread. This inspects related records through a second set of foreign
keys.

### SQL
```sql
SELECT cm.comment_id, t.title, u.full_name AS commenter,
       cm.comment_text, cm.created_at
FROM ticket_comments cm
JOIN tickets t ON cm.ticket_id = t.ticket_id
JOIN users u   ON cm.user_id = u.user_id
ORDER BY cm.created_at;
```

### Output
| comment_id | title | commenter | comment_text | created_at |
| --- | --- | --- | --- | --- |
| 1 | Cannot connect to VPN | Jordan Smith | Confirmed the VPN tunnel establishes but routing to the internal subnet fails. Investigating the split-tunnel configuration. | 2026-05-01 09:40:00 |
| 2 | Cannot connect to VPN | Maya Chen | Still cannot reach the file server after reconnecting to the VPN. | 2026-05-01 10:05:00 |
| 3 | Password reset request | Sofia Garcia | Reset the password and unlocked the account. Asked the user to confirm they can log in. | 2026-05-01 11:00:00 |
| 4 | Password reset request | Liam O'Brien | Confirmed I can log in now. Thank you for the quick help. | 2026-05-01 11:15:00 |
| 5 | Laptop will not power on | Jordan Smith | Ran hardware diagnostics; the battery is not detected. Ordered a replacement battery. | 2026-05-02 09:30:00 |
| 6 | Outlook crashes on launch | Sofia Garcia | Reproduced the crash on a test machine. Reviewing the recent update logs for the mail add-in. | 2026-05-02 14:00:00 |
| 7 | Not receiving external email | Jordan Smith | External mail was being blocked by a misconfigured spam rule. Adjusting the rule now. | 2026-05-03 11:45:00 |
| 8 | Intermittent Wi-Fi drops | Sofia Garcia | Updated the access point firmware in the east wing and am monitoring for further drops. | 2026-05-03 16:30:00 |
| 12 | Intermittent Wi-Fi drops | Noah Kim | Drops are less frequent today but are still happening occasionally. | 2026-05-04 09:10:00 |
| 9 | Access to shared drive denied | Jordan Smith | Added the user to the finance security group; access has been confirmed. | 2026-05-04 10:00:00 |
| 10 | Company-wide network outage on third floor | Jordan Smith | Core switch on the third floor failed over to the backup unit and service was restored. | 2026-05-06 08:35:00 |
| 11 | Company-wide network outage on third floor | Priya Patel | Please document the root cause for the incident report. | 2026-05-06 09:00:00 |

### Explanation
Ordering the joined comments by timestamp reconstructs each ticket's
conversation in sequence. This thread is the main body of text the AI feature
will summarize, so being able to retrieve it reliably is essential.

---

## Query 6: Aggregation

### Purpose
Summarize the tickets table at a glance: how many tickets exist and the span of
dates they cover.

### SQL
```sql
SELECT COUNT(*) AS total_tickets,
       MIN(created_at) AS first_ticket,
       MAX(created_at) AS latest_ticket
FROM tickets;
```

### Output
| total_tickets | first_ticket | latest_ticket |
| --- | --- | --- |
| 10 | 2026-05-01 09:15:00 | 2026-05-06 08:00:00 |

### Explanation
Using `COUNT`, `MIN`, and `MAX` together gives a one-row summary of the table's
size and time range. Aggregates like these feed manager-facing metrics such as
ticket volume and reporting periods.

---

## Query 7: GROUP BY — Tickets by Category

### Purpose
Group tickets by their category to show how the workload is distributed across
issue types.

### SQL
```sql
SELECT c.category_name, COUNT(*) AS ticket_count
FROM tickets t
JOIN categories c ON t.category_id = c.category_id
GROUP BY c.category_name
ORDER BY ticket_count DESC, c.category_name;
```

### Output
| category_name | ticket_count |
| --- | --- |
| Network | 3 |
| Access | 2 |
| Hardware | 2 |
| Software | 2 |
| Email | 1 |

### Explanation
Grouping by category reveals that Network issues are the most common in the
sample data. This is the kind of breakdown a manager dashboard would chart to
spot trends and decide where to focus support resources.

---

## Query 8: AI-Support Retrieval

### Purpose
Assemble the complete evidence bundle for a single selected ticket — its
description, category, priority, status, full comment history, and resolution
notes — exactly as it would be handed to the AI model for summarization. Ticket
10 is used because it has comments and a resolution.

### SQL
```sql
SELECT t.ticket_id, t.title, t.description, t.priority, t.status,
       c.category_name,
       GROUP_CONCAT(cm.comment_text, ' | ') AS comment_history,
       r.resolution_text
FROM tickets t
JOIN categories c            ON t.category_id = c.category_id
LEFT JOIN ticket_comments cm ON t.ticket_id = cm.ticket_id
LEFT JOIN resolutions r      ON t.ticket_id = r.ticket_id
WHERE t.ticket_id = 10
GROUP BY t.ticket_id, t.title, t.description, t.priority, t.status,
         c.category_name, r.resolution_text;
```

### Output
```text
ticket_id        : 10
title            : Company-wide network outage on third floor
description      : Multiple users report a total loss of network connectivity
                   on the third floor of the main building.
priority         : Critical
status           : Resolved
category_name    : Network
comment_history  : Core switch on the third floor failed over to the backup unit
                   and service was restored.
                   | Please document the root cause for the incident report.
resolution_text  : Failed the core switch over to the backup unit, restoring
                   third-floor connectivity.
```

### Explanation
This single query gathers everything the AI feature needs about a ticket into one
row: the structured fields plus the free-text description, the concatenated
comment thread, and the resolution note. A `LEFT JOIN` is used for comments and
resolutions so the query still returns a result for tickets that have neither.
This is the database-resident evidence the model will summarize, and because it
all comes from the database, the AI output can be checked directly against these
fields — keeping the database as the source of truth.
