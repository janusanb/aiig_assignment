# AIIG Deliverables Tracker

A full-stack web application for managing infrastructure project deliverables at Americas Infrastructure Investments Group (AIIG).
## Access here - https://aiig-deliverables-frontend.onrender.com/

## 🎯 Features

### Core Requirements (✅ Implemented)
- **Project Search**: Real-time search for projects by name
- **View Deliverables**: See upcoming deliverables for any project, sorted by due date
- **Data Persistence**: PostgreSQL database with SQLAlchemy ORM
- **Responsive UI**: Clean, professional interface built with React + TypeScript

### Bonus Features (✅ Implemented)
- **Add New Data**: Create new projects, deliverables, and project managers
- **Excel Import**: Upload Excel files to bulk import deliverables with validation
- **Filtering**: Filter by date range, frequency, project manager, status
- **Visual Indicators**: Overdue items highlighted, days-until-due shown

### Future enhancements
- **Calendar feature**: A calendar view (e.g. month/week) so deadlines are discoverable in a more visual way. Users could see due dates on a calendar and click through to deliverables by project or manager.
- **File upload security hardening**: Filename sanitization to prevent path traversal attacks, content-type validation beyond extension checking, and proper sanitization of filenames in saved file paths (currently prefixed but original filename still included).

## 🏗️ Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.12)
- **Database**: PostgreSQL (local via Docker Compose or set `DATABASE_URL`; production on Render)
- **ORM**: SQLAlchemy 2.0
- **Validation**: Pydantic v2
- **Excel Parsing**: pandas + openpyxl

### Frontend
- **Framework**: React 18 + TypeScript
- **Styling**: Native CSS
- **HTTP Client**: Native fetch
- **Build Tool**: Vite

## 📁 Project Structure

```
aiig-deliverables/
├── backend/
│   ├── app/
│   │   ├── api/           # API route handlers
│   │   ├── core/          # Config, database setup
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   └── services/      # Business logic
│   ├── data/              # Database and uploads
│   ├── tests/             # Unit tests
│   ├── seed.py            # Database seeding script
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── services/      # API client
│   │   ├── types/         # TypeScript types
│   │   └── App.tsx
│   └── package.json
└── README.md
```

## 🚀 Quick Start

### One-Click Run (Docker)

If you have [Docker](https://docs.docker.com/get-docker/) and Docker Compose installed:

```bash
docker compose up --build
```

Then open **http://localhost:5173** in your browser. The backend runs on port 8000, the frontend on 5173. A PostgreSQL database runs in a container; the backend connects to it and the app seeds the database automatically on first start if empty.

To seed or reset the database manually: `docker compose run backend python seed.py` (optionally with `--reset` or `--file path/to.xlsx`).

To stop: `Ctrl+C` then `docker compose down`.

### Local development (without Docker)

**Prerequisites:** Python > 3.11 <3.14, Node.js 18+, npm or yarn, and **PostgreSQL** (or use Docker Compose for the database).

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set DATABASE_URL to your PostgreSQL instance (default: postgresql://postgres:postgres@localhost:5432/deliverables)
# export DATABASE_URL=postgresql://user:pass@localhost:5432/deliverables  # if different

# Optionally seed or reset the database before first run
python seed.py   # or python seed.py --reset  or  python seed.py --file path/to.xlsx

# Start the server (database is seeded automatically on first start if empty)
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Alternative Docs: `http://localhost:8000/redoc`

### Running tests

Tests use the database pointed to by `DATABASE_URL`. With Docker Compose, run tests inside the backend container so they use the Compose Postgres:

```bash
docker compose run backend pytest tests/ -v
```

Or, from the `backend/` directory with a local Postgres (and `DATABASE_URL` set):

```bash
cd backend
pytest tests/ -v
```

- **Unit tests** (`tests/unit/`): ProjectService, DeliverableService, ProjectManagerService methods.
- **Behavioral tests** (`tests/behavioral/`): GET endpoints for projects, deliverables, and managers.

Unit tests that create rows in the DB restore it to the base state after the test (reset + re-seed from Excel). Use a dedicated test database (e.g. a separate Postgres DB or `DATABASE_URL` pointing to a test instance) when running tests outside Docker to avoid affecting dev data.

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173`. It expects the backend at `http://localhost:8000` by default; to use a different API URL, set `VITE_API_URL` (e.g. in a `.env` file; see `frontend/.env.example`).


## 📊 API Endpoints

### Projects
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/projects` | List all projects with stats |
| GET | `/api/v1/projects/search?q=` | Search projects by name |
| GET | `/api/v1/projects/{id}` | Get project details |
| GET | `/api/v1/projects/{id}/deliverables` | Get project deliverables |
| POST | `/api/v1/projects` | Create new project |

### Deliverables
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/deliverables` | List all deliverables |
| GET | `/api/v1/deliverables/upcoming?days=30&project_id=&manager_id=&include_overdue=` | Get upcoming deliverables (optional `project_id`, `manager_id`; `days` 1–365, default 30; `include_overdue=true` with `project_id` includes overdue items for that project) |
| GET | `/api/v1/deliverables/overdue` | Get overdue deliverables |
| GET | `/api/v1/deliverables/summary` | Get summary statistics |
| POST | `/api/v1/deliverables` | Create new deliverable |
| POST | `/api/v1/deliverables/filter` | Filter with multiple criteria |

### File Upload (Excel import)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/upload/preview` | Preview Excel file before import (parse → validate → clean; no DB changes) |
| POST | `/api/v1/upload/import` | Import Excel file (parse → validate → clean → load). Duplicates by (project, due_date, frequency, description) are skipped. |
| GET | `/api/v1/upload/template` | Expected columns, valid values (e.g. frequency M/Q/SA/A/OT), and deduplication rule |

The import flow is **parse → validate → clean → load**. Preview uses the same pipeline without writing to the database. The frontend includes an **Import from Excel** tab (file picker, Preview, Import, and result summary).

## 🔐 Security Assumptions (For Discussion)

### Authentication
- Production would implement JWT-based authentication
- Integration with corporate SSO (Azure AD, Okta)
- Role-based access control (Admin, Manager, Viewer)

### Authorization
- Managers can only edit their own projects
- Admins have full access
- Viewers can only read data

### Data Security
- HTTPS in production
- Input validation on all endpoints
- SQL injection prevention via ORM
- File upload validation and scanning
- **Note on file size validation**: The `MAX_UPLOAD_SIZE_MB` setting is defined in configuration (currently 10MB) but not yet enforced before reading files into memory. This was considered during design, which is why the configuration exists, but enforcement should be added as a future enhancement to prevent memory exhaustion from large uploads.

### Deployment
- Container-based deployment (Docker)
- Secrets management via environment variables
- Database connection encryption

## 🔧 Maintenance Assumptions

- **Database Backups**: Daily automated backups
- **Monitoring**: Health checks, error tracking (Sentry)
- **Logging**: Structured logging for debugging
- **Updates**: Semantic versioning, changelog maintenance

## ⚠️ Technical Risks

| Risk | Mitigation |
|------|------------|
| Data loss | Automated backups, transaction logging |
| Performance degradation | Pagination, indexing, caching |
| Security vulnerabilities | Regular updates, security audits |
| Excel format variations | Flexible column mapping, validation |
| Browser compatibility | Modern browsers only, progressive enhancement |

## 📝 Data Model

### Project Manager
- id, name, email, created_at, updated_at

### Project  
- id, name, description, manager_id (FK), created_at, updated_at

### Deliverable
- id, project_id (FK), description, due_date, frequency, status, notes, completed_at, created_at, updated_at

### Frequency Codes
- M = Monthly
- Q = Quarterly
- SA = Semi-Annual
- A = Annual
- OT = One-Time

### Duplicate detection
- **MVP:** Duplicate deliverables are determined by project, due date, frequency, and **description (exact match)**. When creating a deliverable or importing from Excel, an entry that matches an existing one on these four fields is treated as a duplicate and rejected or skipped.
- **Future:** Determining whether two descriptions are semantically the same (e.g. paraphrases) would be handled using **AI, contextual analysis, or an ML system**, rather than a straight string comparison.
