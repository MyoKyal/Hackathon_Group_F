# Charity Donation Matching Platform

AI-powered donation matching system connecting donors, receivers, and volunteers.

## Prerequisites

- Python 3.11+
- PostgreSQL with PostGIS extension (Supabase direct connection string works)
- Node.js 18+ (frontend, Phase 6)

## Backend setup

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env with your DATABASE_URL and secrets
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

```bash
cd frontend
npm install
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
