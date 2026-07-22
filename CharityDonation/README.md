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

## Build phases

This project is built incrementally. See `project_prompt.md` for the full specification.

- **Phase 1** (current): Schema & migrations
- Phase 2: Auth
- Phase 3: Donations & requests
- Phase 4: Matching service
- Phase 5: Deliveries & volunteer flow
- Phase 6: Frontend

## Open items

- Admin role and permissions are undefined; volunteer approval endpoint is a stub.
- JWT logout is client-side only (no server-side token blocklist).
- Stage 2 Gemini integration subject to free-tier rate limits.
