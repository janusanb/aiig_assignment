---
name: AIIG Assignment Compliance Plan
overview: "Ensure the codebase and deliverables fully satisfy the Full Stack Developer Take Home Assignment: Phase 0 restructure repo (backend/ and frontend/ layout); Phase 1 backend core (search project, view upcoming deliverables, data persistence); Phase 2 frontend; optional bonus (add data) and bonus bonus (Excel import); demo prep and evaluation criteria."
todos: []
---

# AIIG Take-Home Assignment — Compliance and Demo Plan

## 0. Core functionality (do this first, backend only)

**Assignment (core):** *"You are hired as a Full Stack Developer at AIIG, and your task is to create a Web Application that optimizes deliverable management and deliver a 15–20-minute demonstration/presentation. The application should allow users to **search for a project** and **view the upcoming deliverables** associated with that project."*

**Priority:** Implement **core functionality first**. Work **completely on the backend first**; do not move to frontend until the backend core is done and verifiable (e.g. via Swagger/curl).

**Core backend scope (Phase 1):**

1. **Search for a project** — API that accepts a search query and returns matching projects (e.g. by name), with enough info to choose one (e.g. project name, manager, deliverable count).
2. **View upcoming deliverables for that project** — API that, given a project id, returns the upcoming deliverables for that project (e.g. due within a configurable window: next 30/60/90 days), sorted by due date, with responsible person (project manager).
3. **Data persistence** — Dataset (project name, deliverable, due date, project manager) loaded into the DB via a one-off seed/import from the provided Excel file; backend uses a persistent store (e.g. SQLite).
4. **Backend runs** — App package layout and run instructions are clear; `seed` then `uvicorn` (or equivalent) works from a clean checkout; APIs are testable via `/docs` or curl.

**After Phase 1 is complete:** Proceed to frontend (so users can search and view upcoming deliverables in the UI), then demo prep, then bonus/bonus-bonus features.

---

## 0b. Restructure repository first (Phase 0 — before any backend build)

**Before** building the backend in any meaningful way, move the appropriate files into the target layout so the repo matches the intended structure. Do this first; then proceed to Phase 1 (backend core).

**Target layout:**

```
aiig-deliverables/          (or repo root: take_home/)
├── backend/
│   ├── app/
│   │   ├── api/             # API route handlers
│   │   ├── core/            # Config, database setup
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   └── services/        # Business logic
│   ├── data/                # Database and uploads (and optionally Excel dataset)
│   ├── tests/               # Unit tests
│   ├── seed.py              # Database seeding script
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API client
│   │   ├── types/           # TypeScript types
│   │   └── App.tsx
│   └── package.json
└── README.md
```

**File moves (current repo root → target):**

| Current location (root) | Target location |
|--------------------------|-----------------|
| main.py | `backend/app/main.py` |
| config.py | `backend/app/core/config.py` |
| database.py | `backend/app/core/database.py` |
| deliverable.py (model) | `backend/app/models/deliverable.py` |
| project.py (model) | `backend/app/models/project.py` |
| project_manager.py (model) | `backend/app/models/project_manager.py` |
| deliverables.py (routes) | `backend/app/api/deliverables.py` |
| projects.py (routes) | `backend/app/api/projects.py` |
| managers.py (routes) | `backend/app/api/managers.py` |
| upload.py (routes) | `backend/app/api/upload.py` |
| deliverable_service.py | `backend/app/services/deliverable_service.py` |
| project_service.py | `backend/app/services/project_service.py` |
| project_manager_service.py | `backend/app/services/project_manager_service.py` |
| excel_service.py | `backend/app/services/excel_service.py` |
| excel.py (Pydantic schemas for Excel) | `backend/app/schemas/excel.py` (or merge into schemas package) |
| seed.py | `backend/seed.py` |
| requirements.txt | `backend/requirements.txt` |
| FSD_deliverable_dataset.xlsx | `backend/data/FSD_deliverable_dataset.xlsx` (optional; or keep at repo root and point seed at it) |

**Additional steps:**

- Create `backend/app/__init__.py`, `backend/app/core/__init__.py`, `backend/app/api/__init__.py`, `backend/app/models/__init__.py`, `backend/app/schemas/__init__.py`, `backend/app/services/__init__.py` so `app` is a package. Ensure `api/__init__.py` wires routers (projects, deliverables, managers, upload); ensure `models/__init__.py` and `schemas/__init__.py` export models and schemas used by routes and services.
- **Schemas:** If project/deliverable/manager request-response schemas live in other files or need to be extracted, add them under `backend/app/schemas/` (e.g. `project.py`, `deliverable.py`, `project_manager.py`) so all `app.schemas` imports resolve.
- Create `backend/data/` (for DB file and optionally the Excel dataset); create `backend/tests/` (placeholder or move existing tests).
- Create `frontend/` with placeholder structure: `frontend/src/components/`, `frontend/src/services/`, `frontend/src/types/`, `frontend/src/App.tsx`, `frontend/package.json` (minimal so the folder exists; real frontend build in Phase 2).
- Update all internal imports to use `app.*` relative to `backend/` as the run root (e.g. `from app.core.config` when running from `backend/`). Seed and main app should run with `backend/` as cwd (or adjust `sys.path` / PYTHONPATH so `app` resolves).
- Leave README.md, Full Stack Developer - Take Home Assigment.pdf, and any top-level docs at repo root; remove or archive duplicated files from root after move so the single source of truth is under `backend/` and `frontend/`.

**Phase 0 done when:** The repo has `backend/` and `frontend/` with the structure above; backend runs from `backend/` (e.g. `cd backend && python seed.py` and `uvicorn app.main:app --reload`); no code remains at repo root that belongs in `backend/app/`.

---

## 1. Requirement mapping (assignment vs current state)

| Requirement | Assignment text | Current state | Action |
|-------------|-----------------|---------------|--------|
| **Core: Search project** | "allow users to search for a project" | Backend: `GET /api/v1/projects/search?q=` | **Phase 1:** Ensure API complete and testable; **Phase 2:** expose in UI |
| **Core: View upcoming deliverables** | "view the upcoming deliverables associated with that project" | Backend: `GET /projects/{id}/deliverables` (all); `GET /deliverables/upcoming?project_id=&days=` | **Phase 1:** Add optional `upcoming_days` (or use existing upcoming endpoint); **Phase 2:** build UI flow |
| **Data persistence** | "persist the data into a backend solution" | SQLite + SQLAlchemy; excel_service.py + seed.py; dataset FSD_deliverable_dataset.xlsx | **Phase 1:** Fix seed path; confirm one-command load from Excel; document run steps |
| **Working application** | "present a working application" | Backend runnable; **no frontend in repo** | **Phase 1:** Backend core done first; **Phase 2:** add minimal frontend (search → select project → upcoming deliverables) |
| **Bonus: Enter data** | Project, Deliverable, Due date, Frequency, PM | Backend: POST projects, deliverables, managers | Optional: add UI or demo via Swagger |
| **Bonus bonus: Excel import** | User uploads Excel → parse, validate, clean, load into DB | Backend: excel_service.py, upload.py (preview/import) | Ensure full pipeline: validations, data cleaning, then load; expose via UI or API |
| **Demo (15–20 min)** | Verbal description of decisions | README has Security, Maintenance, Budget, Risks | Add **Demo script / Evaluation talking points** doc |
| **Code (40 pts)** | Code + documentation | Backend + README present; structure may not match README (no `backend/` or `frontend/` at root) | Align run instructions with actual layout; ensure one-command seed + run |

---

## 2. Critical gaps and fixes

*(Phase 1 = backend only: 2.2, 2.3, 2.4. Phase 2 = frontend: 2.1.)*

### 2.1 Frontend (Phase 2 — after backend core is done)

- **Gap:** README describes React + TypeScript frontend, but there is **no `frontend/` directory** in the repo.
- **Action:** Implement a minimal frontend that:

1. **Search:** Text input → call `GET /api/v1/projects/search?q=...` → show list of projects (name, manager, deliverable count).
2. **Select project:** Click a project → load deliverables for that project.
3. **View upcoming deliverables:** Show deliverables for selected project, with clear "upcoming" framing (e.g. "Due in next 30/60/90 days" or all pending sorted by due date). Prefer calling an endpoint that supports "upcoming" (e.g. `GET /deliverables/upcoming?project_id={id}&days=90`) or add `days` to `GET /projects/{id}/deliverables`.

- **Tech:** Match README (React 18, TypeScript, Vite, Tailwind, Axios) so tech-stack reasoning in the demo is consistent.

### 2.2 "Upcoming" deliverables for a project (Phase 1 — backend)

- **Gap:** Assignment says "view **upcoming** deliverables"; `GET /projects/{id}/deliverables` returns all (pending) deliverables with no time window.
- **Action (choose one):**
- **Option A (recommended):** Add optional query param to `GET /projects/{id}/deliverables`, e.g. `upcoming_days=30` (only deliverables with `due_date` in [today, today+30]). Reuse logic from DeliverableService.get_upcoming.
- **Option B:** Document and use existing `GET /deliverables/upcoming?project_id={id}&days=30`; ensure response includes project manager (who is responsible).

### 2.3 Dataset load and run instructions (Phase 1 — backend)

- **Gap:** seed.py expects `Path(__file__).parent.parent / "data" / "FSD_deliverable_dataset.xlsx"` (i.e. `backend/data/` or similar). Repo has FSD_deliverable_dataset.xlsx at **root**.
- **Action:**
  - Update seed default path to repo root (or a single `data/` at root) so `python seed.py` (or equivalent) runs without extra steps.
  - Document in README: "From repo root: `pip install -r requirements.txt`, `python seed.py`, then start backend." Ensure `requirements.txt` and any `app` package resolution work from that root.

### 2.4 Backend run structure (Phase 0 + Phase 1)

- **Gap:** All backend code imports `app.core`, `app.services`, `app.api`, etc., but project layout shows modules at repo root. README assumes `backend/` with `app/` inside.
- **Action:**
- **Phase 0:** Move all backend files into `backend/app/` per target layout (Section 0b); add `__init__.py`; run from `backend/` so `app` is the package (e.g. `uvicorn app.main:app`, `python seed.py`).
- **Phase 1:** Confirm backend runs from `backend/`; align README Quick Start with `cd backend && ...` and no backend code at repo root.

---

## 3. Evaluation criteria — demo prep (verbal, 15–20 min)

Add a short **DEMO_SCRIPT.md** (or "Evaluation talking points") so you can hit each graded item:

| Criterion | Points | What to say (and where it's documented) |
|-----------|--------|----------------------------------------|
| **(a) Technology stack reasoning** | 15 | Backend: FastAPI (async, OpenAPI, type hints), SQLAlchemy 2 (ORM), Pydantic (validation). Frontend: React 18 + TypeScript (type safety, maintainability), Vite (speed), Tailwind (consistency). DB: SQLite for dev/portability; PostgreSQL-ready for prod. |
| **(b) User experience and usability** | 15 | Single flow: search → select project → see upcoming deliverables; clear labels, responsive layout, error states. (Reference the UI you build.) |
| **(c) Security assumptions** | 10 | Auth: JWT/SSO in prod; RBAC (Admin / Manager / Viewer). Data: HTTPS, validation on inputs, ORM to avoid SQL injection. Deployment: env-based secrets, encrypted DB connections. (Already in README Security section.) |
| **(d) Maintenance assumptions** | 5 | Backups, monitoring, structured logging, semantic versioning. (Already in README Maintenance.) |
| **(e) Budget for product lifecycle** | 5 | One-time build; monthly hosting; ongoing maintenance. (Already in README Budget.) |
| **(f) Technical risks** | 10 | Data loss, performance, security, Excel format drift, browser support; mitigations per README Technical Risks. |
| **Code submission** | 40 | Working app (backend + frontend), README with setup/run, dataset loaded via seed; code organized and documented. |

Structure the doc as bullet points or a 1–2 page script so you can walk through (a)–(f) in order during the demo.

---

## 4. Implementation order

**Phase 0: Restructure repository (do first — before any backend build)**

- Move files into target layout per **Section 0b** above: create `backend/` with `app/api/`, `app/core/`, `app/models/`, `app/schemas/`, `app/services/`; move route handlers, core, models, schemas, services, main.py, seed.py, requirements.txt into place; create `backend/data/`, `backend/tests/`; create `frontend/` placeholder structure.
- Add package `__init__.py` files and fix imports so that running from `backend/` (e.g. `uvicorn app.main:app`, `python seed.py`) works.
- **Phase 0 done when:** Repo matches target layout; backend runs from `backend/`; no duplicate backend code at repo root.

---

**Phase 1: Backend — core only (after Phase 0; finish before frontend)**

1. **Backend run structure**

- Confirm `app` package runs from `backend/` (e.g. `uvicorn app.main:app`). All code now lives under `backend/app/`; no layout fixes needed if Phase 0 was done correctly.
- Document in README: run backend from `backend/` (e.g. `cd backend && pip install -r requirements.txt && python seed.py && uvicorn app.main:app --reload`).

2. **Data persistence (seed from dataset)**

- After Phase 0, seed lives at `backend/seed.py` and dataset at `backend/data/FSD_deliverable_dataset.xlsx` (or repo root). Fix seed.py default path so it loads the Excel file from `backend/data/` (e.g. `Path(__file__).parent / "data" / "FSD_deliverable_dataset.xlsx"`) without manual path hacks.
- Confirm one-command flow from `backend/`: install deps → run seed → DB populated with projects, deliverables, project managers from Excel.
- Ensure excel_service.py (or equivalent) reads the required columns: Project name, deliverable, due date, project manager (and frequency if present).

3. **Search for a project (API)**

- Ensure `GET /api/v1/projects/search?q=<query>` exists and returns matching projects with at least: project id, name, manager name, deliverable count (or equivalent) so a client can list and select a project.
- Verify via Swagger or curl; document in API description if needed.

4. **View upcoming deliverables for that project (API)**

- Provide an API that, given a project id, returns **upcoming** deliverables (e.g. due from today through the next N days). Either:
- Add optional query param to `GET /projects/{id}/deliverables`, e.g. `upcoming_days=30` (or 60/90), reusing DeliverableService.get_upcoming; or
- Document and use existing `GET /deliverables/upcoming?project_id={id}&days=30`.
- Response must include: deliverable description, due date, frequency, and **who is responsible** (project manager name).
- Verify via Swagger or curl.

5. **Phase 1 done when:** From a clean clone, run seed → start backend → open `/docs` → search projects → get project by id → get upcoming deliverables for that project; all succeed with the provided dataset.

---

**Phase 2: Frontend (only after Phase 1 is complete)**

- New `frontend/` (or equivalent) with React + TypeScript + Vite + Tailwind.
- Flows: Search projects → Select project → View upcoming deliverables (and responsible person).
- README updated with frontend install and run.

**Phase 3: Demo and submission**

- Add **DEMO_SCRIPT.md** with talking points for (a)–(f).
- Final pass: backend + seed + frontend from clean clone; verify full user flow; README matches reality.

**Phase 4: Bonus — enter data**

- Optional UI or Swagger demo for adding projects, deliverables, project managers (backend APIs already exist).

**Phase 5: Bonus bonus — Excel import**

- Review and strengthen excel_service.py: validations, data cleaning, then load; optional upload UI.

---

## 5. Bonus bonus: Excel import (parse → validate → clean → load)

**Goal:** When a user provides Excel data, the system should parse it, validate it, clean it, and then load it into the database.

**Pipeline:**

1. **Parse:** Read Excel file (support expected columns: Project name, deliverable/description, due date, project manager, frequency). Handle multiple sheet/header variations if needed.
2. **Validate:** Check required fields present; due dates parseable and valid; frequency codes allowed (M, Q, SA, A, OT); project manager and project names non-empty; reject or flag invalid rows with clear error messages (row/column).
3. **Clean:** Normalize whitespace and casing where appropriate; trim strings; coerce date formats; handle common Excel quirks (e.g. date-as-number); deduplicate or merge by (project, deliverable, due date) per business rules.
4. **Load:** Insert into DB (project managers → projects → deliverables) with transactions; report counts (created/skipped/errors). Optionally support preview (dry-run) before commit.

**Current state:** excel_service.py and upload.py already provide import and preview. Plan is to **review and strengthen** validations and cleaning, then ensure the full flow is documented and (optionally) exposed in the UI.

**Deliverables:**

- Validation layer: required fields, date/frequency/format checks, per-row error reporting.
- Cleaning layer: trim, normalize, date coercion, duplicate handling.
- Single "import" flow: parse → validate → clean → load, with a clear result summary (e.g. imported / skipped / errors).
- Optional: UI to upload Excel and show preview + import result (or keep API-only and demo via Swagger/Postman).

---

## 6. Out of scope (per assignment)

- Slides/reports are **not** required.
- "Security assumptions" are **discussion only** — no auth implementation required in the app.
- Bonus "enter data" is optional; can be demonstrated via API (e.g. Swagger) if no UI is built for it.

---

## 7. Files to add or touch

| Item | File(s) | Purpose |
|------|--------|--------|
| **Phase 0: Restructure** | All backend modules at root | Move into `backend/app/{api,core,models,schemas,services}/`; create `backend/data/`, `backend/tests/`, `frontend/` placeholder; add `__init__.py`; fix imports |
| Frontend | `frontend/` (or documented path) | Search → project → upcoming deliverables UI (Phase 2) |
| Seed path | `backend/seed.py` | Default path to `backend/data/FSD_deliverable_dataset.xlsx` |
| API "upcoming" | projects.py (and possibly deliverable_service.py) | Optional `upcoming_days` on project deliverables |
| Run layout | README.md, config.py if needed | Correct backend/frontend run from repo root (or backend/) |
| Demo prep | **DEMO_SCRIPT.md** (new) | Talking points for (a)–(f) for 15–20 min verbal demo |
| Excel import | excel_service.py, upload.py | Validations, data cleaning, then load; optional upload UI |

This plan ensures every assignment requirement and evaluation criterion is covered, plus the bonus bonus Excel import goal (parse → validate → clean → load), and that you can confidently run and present a working application with clear technical and product reasoning.
