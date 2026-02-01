# AIIG Deliverables Tracker — Demo Script (15–20 min)

Use this script for the verbal demonstration, whether for the hiring panel or internal AIIG stakeholders. Walk through criteria (a)–(f) in order; adjust pacing to fit the time slot.

---

## Intro

- **One sentence:** "This app lets project managers and senior management search for a project and see its upcoming deliverables in one place, so obligations are visible and easier to monitor instead of living in scattered spreadsheets."

---

## (a) Technology stack reasoning (15 pts)

**Talking points (bullets — speak freely):**

- **Backend:** FastAPI for async, automatic OpenAPI docs at `/docs`, and strong type hints. SQLAlchemy 2 for the ORM and Pydantic for request/response validation.
- **Frontend:** React 18 with TypeScript for type safety and maintainability, Vite for fast builds and dev, Tailwind for consistent styling.
- **Database:** PostgreSQL for both local (Docker Compose) and production (Render). Connection string via `DATABASE_URL`; config normalizes `postgres://` to `postgresql://` for providers that use the former.
- **Excel:** pandas and openpyxl for parsing; validation and cleaning live in a dedicated service before load.

---

## (b) User experience and usability (15 pts)

**Talking points (bullets):**

- **Core flow:** Search by project name → select a project → see upcoming deliverables. Single path, no extra clicks.
- **Upcoming view:** 30 / 60 / 90 day window; optional inclusion of overdue items for the selected project so nothing is hidden. Responsible person (project manager) and days-until-due on every row; overdue highlighted.
- **Add data:** Tabs for Add manager, Add project, Add deliverable, and Import from Excel. Covers the bonus “enter data” scenario (e.g. New Toronto Hospital, Submit compliance report, Feb 20 2026, Frequency M, Jane Doe).
- **Excel import:** Choose file → Preview (validation per row) → Import. Result summary shows imported/skipped and created counts. Template endpoint describes columns and rules.
- **Error and empty states:** Clear messages for no results, load failures, and validation errors.

---

## (c) Security assumptions (10 pts)

**Script:**  
"For production we’d assume JWT-based auth or SSO (e.g. Azure AD, Okta) and role-based access: Admin, Manager, Viewer. Managers would be restricted to their own projects; admins full access. All traffic over HTTPS, input validation on every endpoint, and we use the ORM so we don’t hand-write SQL. File uploads are validated by type and size. Deployment would be container-based with secrets in environment variables and encrypted database connections."

**Bullets (if asked):**

- Auth: JWT or SSO; RBAC (Admin / Manager / Viewer).
- Data: HTTPS, validation, ORM (no SQL injection), upload validation.
- Deployment: Docker, env secrets, encrypted DB connections.

---

## (d) Maintenance assumptions (5 pts)

**Script:**  
"We’d run daily automated backups, health checks and error tracking—for example Sentry—and structured logging for debugging. We’d follow semantic versioning and keep a changelog so upgrades and maintenance are predictable."

**Bullets:**

- Backups: daily, automated.
- Monitoring: health checks, error tracking (e.g. Sentry).
- Logging: structured.
- Updates: semantic versioning, changelog.

---

## (e) Budget for product lifecycle (5 pts)

**Script:**  
"Development is a one-time build on the order of about 40 hours. Hosting would run roughly 85 to 325 dollars per month depending on cloud and database choices. Ongoing maintenance for bug fixes and updates we’d estimate at about 400 to 800 dollars per month. The README has the full breakdown."

**Bullets:**

- One-time: ~40 hrs development.
- Monthly hosting: ~$85–325 (cloud, DB, storage/backups).
- Ongoing maintenance: ~$400–800/month (fixes and updates).

---

## (f) Technical risks (10 pts)

**Script:**  
"Main risks we’ve considered: data loss, performance, security, Excel format changes, and browser support. We’d mitigate with automated backups and transaction logging, pagination and indexing, regular security updates, flexible column mapping and validation for Excel, and targeting modern browsers with progressive enhancement where needed. The README has a short table of risks and mitigations."

**Bullets:**

- Data loss → backups, transaction logging.
- Performance → pagination, indexing, caching.
- Security → updates, audits.
- Excel format drift → flexible mapping, validation.
- Browser support → modern browsers, progressive enhancement.

---

## Design decisions / trade-offs

- **PostgreSQL everywhere:** Local development uses PostgreSQL via Docker Compose (one command: `docker compose up`). Production on Render uses the same stack; the ORM and schema work identically in both environments.
- **Upcoming window (30/60/90) and include_overdue:** Configurable window lets users focus on the next 30, 60, or 90 days. Including overdue for the selected project keeps late items visible instead of hiding them once the date has passed.

---

## Future enhancements

- **Authentication and authorization:** Implement JWT or SSO and enforce RBAC (Admin / Manager / Viewer) so the security assumptions become real.
- **Calendar view:** Month/week calendar of due dates so deadlines are discoverable in a more visual way (e.g. click a date to see deliverables, filter by project or manager).
- **Notifications:** Reminders (e.g. email or in-app) for upcoming or overdue deliverables.
- **Reporting:** Export or dashboards (e.g. by manager, by project, compliance over time).

---

*Reference: README (Security, Maintenance, Budget, Technical Risks), PLAN.md (evaluation criteria).*
