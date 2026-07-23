# Charity Donation Matching Platform

AI-powered donation matching system connecting donors, receivers, and volunteers.

## Prerequisites

- Python 3.11+
- PostgreSQL with PostGIS extension (Supabase direct connection string works)
- Node.js 18+ (frontend, Phase 6)

## Backend setup

Dependencies are declared in `backend/pyproject.toml` (Python 3.11 or 3.12 — **not 3.14**, which has no wheels for the pinned deps).

**With [uv](https://docs.astral.sh/uv/) (recommended — creates the venv, resolves from `uv.lock`, installs, all in one step):**

```bash
cd backend
uv sync --extra dev            # creates .venv + installs runtime + test deps
cp .env.example .env           # then fill in DATABASE_URL + a real JWT_SECRET
# run commands via:  uv run uvicorn app.main:app --reload
# or activate:       .venv\Scripts\activate   (source .venv/bin/activate on macOS/Linux)
```

**With plain pip/venv:**

```bash
cd backend
py -3.12 -m venv .venv         # Windows: use the py launcher to pick 3.12
# python3.12 -m venv .venv     # macOS/Linux

# Activate the venv:
.venv\Scripts\activate         # Windows (PowerShell/cmd)
source .venv/bin/activate      # macOS/Linux

pip install -e ".[dev]"        # installs runtime + test deps from pyproject.toml
cp .env.example .env
# Edit .env with your DATABASE_URL and secrets (set a real JWT_SECRET)
```

Run migrations:

```bash
alembic upgrade head
```

Start the API:

```bash
uvicorn app.main:app --reload
```

## Frontend setup

Dependencies are declared in `frontend/package.json` (Node 18+). There is no toml — `package.json` is the manifest, and `npm install` is the "activate" step.

```bash
cd frontend
npm install                    # installs everything from package.json
cp .env.example .env
# Edit .env if backend isn't on localhost:8000
npm run dev
```

## Build phases

This project is built incrementally. See `project_prompt.md` for the full specification.

- Phase 1: Schema & migrations — done
- Phase 2: Auth — done
- Phase 3: Donations & requests — done
- Phase 4: Matching service — done
- Phase 5: Deliveries & volunteer flow — done
- Phase 6: Frontend — done

## Open items

- Admin role and permissions are undefined; volunteer approval endpoint is a stub.
- JWT logout is client-side only (no server-side token blocklist).
- Stage 2 Gemini integration subject to free-tier rate limits.
