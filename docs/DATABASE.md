# Database schema / data dictionary

**Engine:** SQLite 3  
**Default file:** `data/app.db` (locally generated and excluded from Git)  
**Schema initializer:** `app/database.py::initialize()`

## `leads`
| Field | SQLite type | Meaning |
|---|---|---|
| `id` | INTEGER PRIMARY KEY | Auto-increment lead reference |
| `company` | TEXT NOT NULL | Organization name |
| `contact` | TEXT NOT NULL | Contact person's display name |
| `email` | TEXT NOT NULL | Contact email, may be empty if phone provided |
| `phone` | TEXT NOT NULL | Contact phone, may be empty if email provided |
| `service_interest` | TEXT NOT NULL | Enum from request schema |
| `budget_range` | TEXT NOT NULL | Illustrative sales budget band |
| `timeline` | TEXT NOT NULL | Prospect's stated timescale |
| `source` | TEXT NOT NULL | Origination channel |
| `message` | TEXT NOT NULL | Optional project brief |
| `consent` | INTEGER NOT NULL | 0/1 boolean recorded on submission |
| `status` | TEXT NOT NULL | Pipeline stage; initially `new` |
| `score` | INTEGER NOT NULL | Rule-based score, 0–100 |
| `priority` | TEXT NOT NULL | Hot/warm/cold category |
| `next_followup_at` | TEXT nullable | ISO 8601 timestamp in UTC |
| `created_at` | TEXT NOT NULL | Creation timestamp, UTC |
| `updated_at` | TEXT NOT NULL | Modification timestamp, UTC |

Indexes: status, priority, follow-up time.

## `activities`
| Field | SQLite type | Meaning |
|---|---|---|
| `id` | INTEGER PRIMARY KEY | Unique event ID |
| `lead_id` | INTEGER NOT NULL | Parent lead; foreign key, `ON DELETE CASCADE` |
| `kind` | TEXT NOT NULL | `created`, `updated`, `note` |
| `note` | TEXT NOT NULL | Displayable internal note/event text |
| `created_at` | TEXT NOT NULL | Event timestamp, UTC |

Index: lead ID.

## Retention and deletion
Deletion from the admin UI removes the lead and linked activity notes. Backups and external copies are outside this application; if you make any, manage deletion there separately. No scheduled retention policy is implemented. Never commit `data/app.db` to public GitHub.

## Schema and backup notes
The schema is created with `CREATE TABLE IF NOT EXISTS`; no migration mechanism or automatic backup currently exists. Stop the app and back up `data/app.db` before any schema change. Protect any database copy containing personal data.
