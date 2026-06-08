# Schema Verification

These queries confirm that the database builds successfully and contains
internally consistent seed data. All results below were produced by running
the queries against `data/project.db` after `python seed.py`.

## 1. Row counts per table

```sql
SELECT 'users' AS table_name, COUNT(*) AS rows FROM users
UNION ALL SELECT 'categories', COUNT(*) FROM categories
UNION ALL SELECT 'tags', COUNT(*) FROM tags
UNION ALL SELECT 'tickets', COUNT(*) FROM tickets
UNION ALL SELECT 'ticket_comments', COUNT(*) FROM ticket_comments
UNION ALL SELECT 'resolutions', COUNT(*) FROM resolutions
UNION ALL SELECT 'ticket_tags', COUNT(*) FROM ticket_tags
UNION ALL SELECT 'ticket_status_history', COUNT(*) FROM ticket_status_history
UNION ALL SELECT 'ai_summaries', COUNT(*) FROM ai_summaries;
```

| table_name | rows |
| --- | --- |
| users | 6 |
| categories | 5 |
| tags | 6 |
| tickets | 10 |
| ticket_comments | 12 |
| resolutions | 4 |
| ticket_tags | 12 |
| ticket_status_history | 13 |
| ai_summaries | 3 |

Total: **71 records** across 9 tables (well above the 20-record minimum).

## 2. Tickets by status

```sql
SELECT status, COUNT(*) AS ticket_count
FROM tickets
GROUP BY status
ORDER BY ticket_count DESC;
```

| status | ticket_count |
| --- | --- |
| Resolved | 3 |
| Open | 3 |
| In Progress | 2 |
| New | 1 |
| Closed | 1 |

## 3. Tickets by priority

```sql
SELECT priority, COUNT(*) AS ticket_count
FROM tickets
GROUP BY priority
ORDER BY ticket_count DESC;
```

| priority | ticket_count |
| --- | --- |
| Medium | 4 |
| High | 3 |
| Low | 2 |
| Critical | 1 |

## 4. Resolved versus unresolved tickets (LEFT JOIN)

```sql
SELECT CASE WHEN r.ticket_id IS NULL THEN 'Unresolved' ELSE 'Has resolution' END AS state,
       COUNT(*) AS ticket_count
FROM tickets t
LEFT JOIN resolutions r ON t.ticket_id = r.ticket_id
GROUP BY state;
```

| state | ticket_count |
| --- | --- |
| Has resolution | 4 |
| Unresolved | 6 |

## 5. Comment count per ticket (JOIN + aggregate)

```sql
SELECT t.ticket_id, t.title, COUNT(c.comment_id) AS comments
FROM tickets t
LEFT JOIN ticket_comments c ON t.ticket_id = c.ticket_id
GROUP BY t.ticket_id, t.title
ORDER BY comments DESC, t.ticket_id
LIMIT 5;
```

| ticket_id | title | comments |
| --- | --- | --- |
| 1 | Cannot connect to VPN | 2 |
| 2 | Password reset request | 2 |
| 6 | Intermittent Wi-Fi drops | 2 |
| 10 | Company-wide network outage on third floor | 2 |
| 3 | Laptop will not power on | 1 |

## 6. Tags per ticket (many-to-many through ticket_tags)

```sql
SELECT t.ticket_id, t.title, GROUP_CONCAT(g.tag_name, ', ') AS tags
FROM tickets t
JOIN ticket_tags tt ON t.ticket_id = tt.ticket_id
JOIN tags g ON tt.tag_id = g.tag_id
GROUP BY t.ticket_id, t.title
ORDER BY t.ticket_id
LIMIT 5;
```

| ticket_id | title | tags |
| --- | --- | --- |
| 1 | Cannot connect to VPN | vpn, recurring |
| 2 | Password reset request | password-reset, onboarding |
| 3 | Laptop will not power on | hardware-failure |
| 4 | Outlook crashes on launch | recurring |
| 5 | Not receiving external email | recurring |

A `PRAGMA foreign_key_check;` run at the end of `seed.py` returns no rows,
confirming there are no dangling foreign keys.
