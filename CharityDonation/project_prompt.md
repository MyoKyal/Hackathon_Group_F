# Build prompt: AI-powered donation matching system

## Project summary

Build a full-stack donation matching platform. Donors submit donations (optionally targeting a specific receiver). Receivers submit requests for items they need. A hybrid matching service — rules-based pre-filtering followed by Gemini for final selection — pairs donations to receiver requests, then selects the best-suited volunteer to transport the donation. Volunteers can accept or decline assignments. A delivery is only marked complete when both the volunteer and the receiver confirm it.

There is no admin role yet — do not invent one or add admin-only functionality beyond the single stubbed approval endpoint described below. All users are a single `user` role by default and can act as both donor and receiver freely — there is no separate donor/receiver account type. Volunteer is an elevated status a user applies for on top of their base account; it is not a separate signup type.

## Tech stack

- Frontend: React (Vite + TypeScript), React Router, TanStack Query for server state, plain CSS modules or Tailwind — keep it minimal
- Backend: FastAPI (Python 3.11+), Pydantic v2 for schemas
- ORM / migrations: SQLAlchemy 2.0 + Alembic
- Database: PostgreSQL with PostGIS extension, hosted on Supabase (connect via direct Postgres connection string, not the Supabase client SDK)
- Auth: custom JWT auth in FastAPI, `python-jose` for tokens, `passlib[bcrypt]` for password hashing
- Spatial: GeoAlchemy2 for PostGIS integration in SQLAlchemy models
- Matching: two-stage hybrid. Stage 1 is deterministic rules-based scoring (keyword/category match + PostGIS distance) that narrows candidates to a shortlist. Stage 2 sends that shortlist to Gemini (`google-generativeai` SDK, model `gemini-2.0-flash` or current free-tier flash model — check availability at build time) to pick/rank the final match with a short reasoning string. API key from env var, never hardcoded. If Gemini fails or times out (5s max), fall back to Stage 1's top-scored candidate.

Do not set up Docker, deployment configs, or hosting — local dev setup only. Provide `requirements.txt` (backend), `package.json` (frontend), `.env.example` for both, and a top-level `README.md` with local run instructions.

## Repository structure

```
/
├── backend/
│   ├── alembic/
│   │   ├── versions/
│   │   └── env.py
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                # FastAPI app entrypoint
│   │   ├── config.py              # Settings via pydantic-settings
│   │   ├── db.py                  # Engine, SessionLocal, Base
│   │   ├── deps.py                # Common FastAPI dependencies (get_db, get_current_user)
│   │   ├── models/                # SQLAlchemy models, one file per aggregate
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── donation.py
│   │   │   ├── receiver_request.py
│   │   │   ├── delivery.py
│   │   │   └── volunteer_decline.py
│   │   ├── schemas/               # Pydantic v2 request/response schemas
│   │   │   ├── auth.py
│   │   │   ├── donation.py
│   │   │   ├── request.py
│   │   │   ├── volunteer.py
│   │   │   └── delivery.py
│   │   ├── routers/               # FastAPI routers by domain
│   │   │   ├── auth.py
│   │   │   ├── donations.py
│   │   │   ├── requests.py
│   │   │   ├── matching.py
│   │   │   ├── volunteers.py
│   │   │   └── deliveries.py
│   │   ├── services/              # Business logic, isolated from routers
│   │   │   ├── auth_service.py
│   │   │   ├── donation_service.py
│   │   │   ├── request_service.py
│   │   │   ├── matching/          # Matching stays as a subfolder — it's the biggest
│   │   │   │   ├── __init__.py
│   │   │   │   ├── stage1_rules.py     # Deterministic scoring, isolated & tunable
│   │   │   │   ├── stage2_gemini.py    # Gemini prompt + parsing, isolated
│   │   │   │   └── orchestrator.py     # Ties Stage 1 + Stage 2 + fallback
│   │   │   └── delivery_service.py
│   │   └── core/
│   │       ├── security.py        # JWT encode/decode, password hashing
│   │       └── exceptions.py      # Custom exception classes + handlers
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_donations.py
│   │   ├── test_matching_stage1.py
│   │   └── test_deliveries.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── api/                   # API client wrapper, one file per resource
│   │   │   ├── client.ts          # Axios/fetch wrapper with auth header injection
│   │   │   ├── auth.ts
│   │   │   ├── donations.ts
│   │   │   ├── requests.ts
│   │   │   ├── volunteers.ts
│   │   │   └── deliveries.ts
│   │   ├── contexts/
│   │   │   └── AuthContext.tsx    # Current user + token state
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   └── useVolunteerStatus.ts
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── Header.tsx
│   │   │   │   └── ProtectedRoute.tsx
│   │   │   ├── forms/
│   │   │   │   ├── DonationForm.tsx
│   │   │   │   ├── RequestForm.tsx
│   │   │   │   └── LocationPicker.tsx
│   │   │   └── ui/                # Buttons, cards, badges — keep minimal
│   │   ├── pages/
│   │   │   ├── LoginPage.tsx
│   │   │   ├── SignupPage.tsx
│   │   │   ├── HomePage.tsx
│   │   │   ├── DonatePage.tsx
│   │   │   ├── RequestPage.tsx
│   │   │   ├── MyDonationsPage.tsx
│   │   │   ├── MyRequestsPage.tsx
│   │   │   ├── VolunteerApplyPage.tsx
│   │   │   ├── VolunteerDashboardPage.tsx
│   │   │   └── DeliveryDetailPage.tsx
│   │   └── types/                 # Shared TS types (matches backend Pydantic)
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── .env.example
└── README.md
```

## Volunteer application

Any user can apply to become a volunteer via `POST /volunteers/apply`. This sets `is_volunteer = false` initially and `volunteer_status = pending` on their user record. A stubbed `POST /volunteers/{user_id}/approve` endpoint flips `volunteer_status` to `approved` and `is_volunteer` to `true` — this endpoint has no role/permission check yet since there is no admin system; note clearly in code comments that this is an open gap requiring real admin gating later. Only users with `is_volunteer = true` and `volunteer_status = approved` are eligible for matching/assignment.

## Core workflow (must match exactly)

1. **Donor submits a donation**: item details (name, category, description, quantity), pickup location (lat/lng), and optionally checks "target a receiver."
   - If checked, the frontend calls `GET /donations/matches` to show a live-filtered list of open receiver requests matching the item details already entered.
     - If the donor picks one → skip matching logic entirely, create a delivery record directly for that donor-receiver pair, then go to volunteer selection.
     - If no matches are shown → falls through to the untargeted flow below.
   - If not checked (or falls through) → donation enters the untargeted pool.
2. **Untargeted pool**: matching service scores open receiver requests using Stage 1 rules-based scoring (see formula below), takes the top N candidates, sends them to Gemini (Stage 2) for final selection with reasoning. Falls back to top Stage 1 candidate if Gemini fails.
   - Match found → create delivery record, proceed to volunteer selection.
   - No match found → donation stays in `pending` status. Event-triggered: whenever a new receiver request is created via `POST /requests`, the matching service re-scores all pending donations against the new request.
3. **Volunteer selection**: for a delivery record, matching service filters candidates to approved + available volunteers who have not already declined this specific delivery, ranks them by Stage 1 (proximity), sends top N to Gemini (Stage 2). Falls back to closest Stage 1 candidate on Gemini failure.
4. **Volunteer notified**:
   - Accept → volunteer is assigned, delivery status → `in_transit`.
   - Decline → decline is recorded in `volunteer_declines` table, matching service is re-invoked excluding declined volunteers.
5. **Delivery completion**: requires both `volunteer_confirmed` and `receiver_confirmed` to be true before delivery status becomes `completed`. Track as two independent boolean fields.

## Database schema (exact)

### `users`
| column | type | constraints |
|---|---|---|
| id | UUID | PK, default `gen_random_uuid()` |
| email | VARCHAR(255) | UNIQUE, NOT NULL |
| password_hash | VARCHAR(255) | NOT NULL |
| full_name | VARCHAR(255) | NOT NULL |
| phone | VARCHAR(32) | nullable |
| base_location | `geography(Point, 4326)` | nullable |
| is_volunteer | BOOLEAN | NOT NULL, default `false` |
| volunteer_status | ENUM('none','pending','approved','rejected') | NOT NULL, default `'none'` |
| is_available | BOOLEAN | NOT NULL, default `true` |
| created_at | TIMESTAMPTZ | NOT NULL, default `now()` |

Indexes: `email` (unique), GIST index on `base_location`.

### `donations`
| column | type | constraints |
|---|---|---|
| id | UUID | PK |
| donor_id | UUID | FK → users.id, NOT NULL, ON DELETE CASCADE |
| item_name | VARCHAR(255) | NOT NULL |
| item_category | VARCHAR(64) | NOT NULL |
| description | TEXT | nullable |
| quantity | INTEGER | NOT NULL, default 1, CHECK > 0 |
| pickup_location | `geography(Point, 4326)` | NOT NULL |
| target_receiver_id | UUID | FK → users.id, nullable |
| status | ENUM('pending','matched','in_transit','completed') | NOT NULL, default `'pending'` |
| created_at | TIMESTAMPTZ | NOT NULL, default `now()` |

Indexes: `donor_id`, `status`, GIST on `pickup_location`.

### `receiver_requests`
| column | type | constraints |
|---|---|---|
| id | UUID | PK |
| requester_id | UUID | FK → users.id, NOT NULL, ON DELETE CASCADE |
| item_name | VARCHAR(255) | NOT NULL |
| item_category | VARCHAR(64) | NOT NULL |
| description | TEXT | nullable |
| quantity_needed | INTEGER | NOT NULL, default 1, CHECK > 0 |
| location | `geography(Point, 4326)` | NOT NULL |
| status | ENUM('open','matched','fulfilled') | NOT NULL, default `'open'` |
| created_at | TIMESTAMPTZ | NOT NULL, default `now()` |

Indexes: `requester_id`, `status`, GIST on `location`.

### `deliveries`
| column | type | constraints |
|---|---|---|
| id | UUID | PK |
| donation_id | UUID | FK → donations.id, UNIQUE, NOT NULL |
| receiver_request_id | UUID | FK → receiver_requests.id, nullable (null if donor targeted a specific user without an existing request) |
| receiver_id | UUID | FK → users.id, NOT NULL |
| volunteer_id | UUID | FK → users.id, nullable (null until volunteer accepts) |
| stage1_score | FLOAT | nullable |
| gemini_reasoning | TEXT | nullable |
| status | ENUM('awaiting_volunteer','in_transit','completed','cancelled') | NOT NULL, default `'awaiting_volunteer'` |
| volunteer_confirmed | BOOLEAN | NOT NULL, default `false` |
| receiver_confirmed | BOOLEAN | NOT NULL, default `false` |
| created_at | TIMESTAMPTZ | NOT NULL, default `now()` |
| completed_at | TIMESTAMPTZ | nullable |

Indexes: `donation_id` (unique), `volunteer_id`, `receiver_id`, `status`.

### `volunteer_declines`
| column | type | constraints |
|---|---|---|
| id | UUID | PK |
| delivery_id | UUID | FK → deliveries.id, NOT NULL, ON DELETE CASCADE |
| volunteer_id | UUID | FK → users.id, NOT NULL |
| declined_at | TIMESTAMPTZ | NOT NULL, default `now()` |

Composite unique constraint on `(delivery_id, volunteer_id)`. Indexes on both FKs.

The first Alembic migration must run `CREATE EXTENSION IF NOT EXISTS postgis;` before creating any tables.

## Matching logic (exact)

### Stage 1: donor-receiver rules-based scoring

For each open receiver_request R, given a donation D:

```
category_match = 1.0 if D.item_category == R.item_category else 0.0
keyword_score = jaccard_similarity(tokenize(D.item_name + " " + D.description),
                                   tokenize(R.item_name + " " + R.description))
distance_meters = ST_Distance(D.pickup_location, R.location)
distance_score = 1.0 / (1.0 + distance_meters / 1000.0)   # decays with km

score = 0.5 * category_match + 0.3 * keyword_score + 0.2 * distance_score
```

Filter out any request where `category_match == 0 AND keyword_score < 0.2` (hard rule: totally unrelated items should never appear).

Take top N=5 candidates (or fewer if less exist) to send to Stage 2.

### Stage 1: volunteer ranking

For each approved + available volunteer V (excluding those in `volunteer_declines` for this delivery), given donation pickup location P:

```
distance_meters = ST_Distance(V.base_location, P)
distance_score = 1.0 / (1.0 + distance_meters / 1000.0)
score = distance_score
```

Take top N=5. If a volunteer has no `base_location` set, exclude them.

### Stage 2: Gemini prompt template

Isolate the prompt in `stage2_gemini.py` as a constant string with `.format()` placeholders. Example structure — refine wording during build:

```
You are helping match a donation to the best receiver request.

DONATION:
- Item: {item_name}
- Category: {category}
- Description: {description}

CANDIDATE REQUESTS (pre-filtered, top {n}):
{numbered_list_of_candidates_with_scores}

Select the single best match by number and give a one-sentence reason.
Respond in strict JSON: {{"selected_index": <int>, "reason": "<string>"}}
```

Volunteer prompt follows the same shape (donation + candidate volunteers with distance + availability, select best + reason).

Call with 5-second timeout. If timeout, JSON parse error, or any exception → log and use the top Stage 1 candidate. Store the Stage 1 score and (if Gemini succeeded) the reason string on the delivery record.

## API surface (with request/response shapes)

All requests/responses use JSON. All authenticated endpoints require `Authorization: Bearer <jwt>`. Timestamps are ISO 8601 UTC.

### Auth

**POST /auth/signup**
```json
Request:  { "email": "a@b.com", "password": "...", "full_name": "...", "phone": "..." }
Response: 201 { "id": "uuid", "email": "...", "full_name": "...", "access_token": "...", "token_type": "bearer" }
Errors:   409 if email exists, 422 on validation
```

**POST /auth/login**
```json
Request:  { "email": "...", "password": "..." }
Response: 200 { "access_token": "...", "token_type": "bearer", "user": { "id": "...", "email": "...", "full_name": "...", "is_volunteer": bool, "volunteer_status": "..." } }
Errors:   401 on bad credentials
```

**POST /auth/logout** — 204. (Client discards token; server has nothing to invalidate without a token blocklist, which is out of scope. Document this.)

**GET /auth/me** — 200 returns current user object (same shape as login `user`).

### Donations

**POST /donations**
```json
Request:  { "item_name": "...", "item_category": "...", "description": "...", "quantity": 1,
            "pickup_location": { "lat": 1.234, "lng": 5.678 },
            "target_receiver_id": "uuid-or-null" }
Response: 201 { "id": "uuid", "status": "pending|matched", ... full donation object,
                "delivery": { ...if matched immediately... } | null }
```
On submit: if `target_receiver_id` provided, create delivery directly (skip matching). Otherwise trigger Stage 1 + Stage 2 matching against open requests. If match found, create delivery and set donation status to `matched`.

**GET /donations** — 200 returns list of current user's donations, newest first.

**GET /donations/{id}** — 200 returns donation + linked delivery if exists. 404 if not owned by current user (do not leak existence).

**GET /donations/matches?item_name=...&item_category=...&lat=...&lng=...** — used by the "target a receiver" UI. Runs Stage 1 scoring only (no Gemini call — this is a preview) and returns top 10 open receiver requests. 200 returns array of `{ request_id, requester_name, item_name, distance_km, score }`.

### Receiver requests

**POST /requests**
```json
Request:  { "item_name": "...", "item_category": "...", "description": "...",
            "quantity_needed": 1, "location": { "lat": ..., "lng": ... } }
Response: 201 full request object
```
On submit: also trigger re-matching of any donations with status=`pending`, in case this new request enables a match.

**GET /requests** — current user's requests.

**GET /requests/{id}** — 404 if not owned.

**PATCH /requests/{id}** — allowed fields: `description`, `quantity_needed`, `status` (only `open` → `fulfilled` allowed by owner; other transitions rejected 400).

### Matching (internal, exposed for debugging)

**POST /matching/donor-receiver** — body `{ "donation_id": "uuid" }`. Runs full matching flow, returns result.
**POST /matching/volunteer** — body `{ "delivery_id": "uuid" }`. Runs volunteer selection.
**POST /matching/volunteer/next** — body `{ "delivery_id": "uuid" }`. Re-runs after a decline.
**GET /matching/pending** — lists donations with status=`pending`. Debugging aid.

Note in code comments: these are internal service functions exposed as endpoints for debugging. No role gate yet — flag as open item.

### Volunteers

**POST /volunteers/apply** — 200 `{ "volunteer_status": "pending" }`. Requires user not already applied/approved (409 if so).

**POST /volunteers/{user_id}/approve** — 200 updated user object. NO permission check — see open items.

**GET /volunteers/assignments** — 200 array of deliveries where current user is `volunteer_id` OR delivery is currently offered to them (status `awaiting_volunteer` and they're the current pick). Include donation + receiver summary.

**POST /volunteers/assignments/{delivery_id}/accept** — 200. Sets `volunteer_id`, delivery status → `in_transit`, donation status → `in_transit`. 409 if already accepted by another volunteer.

**POST /volunteers/assignments/{delivery_id}/decline** — 200. Records in `volunteer_declines`, re-triggers `matching/volunteer/next`. 409 if already accepted.

### Deliveries

**GET /deliveries/{id}** — 200 full delivery detail. 404 if user is not donor, receiver, or assigned volunteer.

**POST /deliveries/{id}/confirm-volunteer** — 200. Only the assigned volunteer can call. Sets `volunteer_confirmed = true`. If `receiver_confirmed` also true, status → `completed`, `completed_at` set, donation status → `completed`, request status → `fulfilled`.

**POST /deliveries/{id}/confirm-receiver** — 200. Only the receiver can call. Same dual-check logic.

## Error handling conventions

- Use FastAPI's `HTTPException` for domain errors; custom exception classes in `core/exceptions.py` that map to status codes via exception handlers registered in `main.py`.
- Standard error response shape: `{ "detail": "<message>", "code": "<snake_case_error_code>" }`.
- Status codes:
  - 400: invalid state transition (e.g. patching a fulfilled request back to open)
  - 401: missing/invalid token
  - 403: authenticated but not permitted (e.g. non-donor calling donor-only endpoint)
  - 404: resource not found OR not owned (do not distinguish — prevents enumeration)
  - 409: conflict (email exists, delivery already accepted, already applied as volunteer)
  - 422: Pydantic validation error (automatic from FastAPI)
  - 500: unexpected — log with traceback, return generic message
- No stack traces in responses. Log everything server-side with `logging` module.
- All 4xx errors must include the `code` field for frontend to switch on.

## Frontend requirements (details)

- Vite + TypeScript + React Router v6.
- TanStack Query for all server state. No Redux/Zustand for server data. Local UI state via `useState`.
- `AuthContext` provides `{ user, token, login, logout, signup }`. Token stored in `localStorage`. On mount, if token exists, call `/auth/me` to hydrate user.
- `ProtectedRoute` component wraps routes needing auth. `VolunteerRoute` variant additionally requires `is_volunteer && volunteer_status === 'approved'`.
- API client (`api/client.ts`) is a thin wrapper injecting auth header and parsing the `{ detail, code }` error shape into a typed error class.
- Location picker: for the hackathon MVP, use a simple form with lat/lng number inputs plus a "use my location" button that calls `navigator.geolocation`. Do not integrate a map library unless time permits — flag it if skipped.
- Live match preview on `DonatePage`: as donor fills form, debounce 500ms and call `GET /donations/matches` if "target receiver" is checked. Show results as selectable cards. Selecting one populates `target_receiver_id` on submit.
- Volunteer dashboard: poll `GET /volunteers/assignments` every 15s via TanStack Query `refetchInterval`. Show current offer prominently with accept/decline buttons. Show active assignment with "mark delivered" button.
- Style: minimal. One color for primary actions, one for destructive, gray for neutral. No design system needed.

## Testing requirements

Backend (`pytest`, `pytest-asyncio`, `httpx.AsyncClient`):
- `conftest.py` provides a fixture that spins up a test DB (separate schema or DB), runs migrations, and rolls back per test.
- `test_auth.py`: signup happy path, duplicate email 409, login happy path, bad password 401, `/auth/me` requires token.
- `test_donations.py`: create donation, list only returns own donations, get by id 404 for other user's donation.
- `test_matching_stage1.py`: unit tests for the scoring formula — verify category match dominates, distance decay is monotonic, keyword jaccard is symmetric. Test the hard filter (unrelated items excluded). Do NOT test Stage 2 (Gemini) — mock the module boundary; testing an external API is out of scope.
- `test_deliveries.py`: dual-confirmation logic — only-volunteer-confirmed stays `in_transit`, only-receiver-confirmed stays `in_transit`, both → `completed`.

No coverage target required; the above tests are the minimum bar.

Frontend: skip unit tests. Manually verify each page works end-to-end against the backend before considering phases complete.

## Build sequence — work in phases, stop after each for review

Do not attempt all of this in one pass. Work through these phases in order. After each phase: (a) verify the acceptance criteria yourself, (b) summarize what was built + any assumptions made, (c) wait for confirmation before continuing.

### Phase 1 — Schema & migrations
Build: SQLAlchemy models, GeoAlchemy2 setup, Alembic init + first migration.
Acceptance:
- `alembic upgrade head` succeeds on a fresh database.
- `CREATE EXTENSION postgis` runs before any table creation.
- All tables, columns, types, indexes, and FKs match the schema section exactly.
- Enums are created as native Postgres ENUM types, not VARCHAR with CHECK.

### Phase 2 — Auth
Build: signup, login, logout, `/auth/me`, JWT encode/decode in `core/security.py`, `get_current_user` dependency in `deps.py`.
Acceptance:
- Passwords stored as bcrypt hashes, never plaintext.
- JWT includes `sub` (user id) and `exp`. Reject expired.
- `test_auth.py` passes.
- Manual: can signup, login, and hit `/auth/me` with token in HTTP client.

### Phase 3 — Donations & requests
Build: `POST/GET /donations`, `POST/GET/PATCH /requests`, `GET /donations/matches` (Stage 1 preview only).
Acceptance:
- `test_donations.py` passes.
- Cannot see other users' donations or requests.
- `GET /donations/matches` returns top 10 open requests sorted by Stage 1 score.
- Creating a receiver request logs (or invokes) re-matching of pending donations (can be a no-op stub in this phase, wired up in Phase 4).

### Phase 4 — Matching service
Build: `services/matching/stage1_rules.py`, `stage2_gemini.py`, `orchestrator.py`, `/matching/*` endpoints, integration into donation creation flow.
Acceptance:
- `test_matching_stage1.py` passes.
- Gemini failure (mock a raised exception) falls back to Stage 1 top candidate.
- Gemini success stores `gemini_reasoning` on the delivery.
- Creating a request now re-matches pending donations (wired from Phase 3 stub).
- Env var `GEMINI_API_KEY` documented in `.env.example`.

### Phase 5 — Deliveries & volunteer flow
Build: `POST /volunteers/apply`, `POST /volunteers/{id}/approve`, assignment accept/decline, decline history + re-matching, dual-confirmation.
Acceptance:
- `test_deliveries.py` passes.
- Decline re-triggers volunteer selection excluding declined volunteers.
- Both confirmations required for `completed` status; setting one alone keeps status `in_transit`.
- Volunteer approval endpoint has a `# TODO: no permission check — see open items` comment.

### Phase 6 — Frontend
Build: full React app per the frontend section.
Acceptance:
- Can signup, login, submit a donation (both targeted and untargeted), submit a request, apply as volunteer.
- After stub-approving a volunteer via backend endpoint, that user sees assignments and can accept/decline/confirm delivery.
- Live match preview works with 500ms debounce.
- No console errors on happy path flows.

## Open items to flag, not solve

Report these in each phase summary if relevant:
- Admin role and permissions are undefined. The volunteer-approval endpoint is a temporary stub with no access control — known security gap, not a design decision.
- Volunteer availability model — using a simple `is_available` boolean; real scheduling / max-concurrent-jobs logic undecided.
- Stage 1 scoring weights (0.5 category, 0.3 keywords, 0.2 distance) are reasonable defaults, not empirically tuned.
- Stage 2 Gemini prompt is a first pass — shortlist size, field selection, and reasoning parsing may need iteration.
- Gemini free-tier rate limits are not accounted for. No queuing/backoff — a burst of matching calls during demo could hit limits.
- JWT logout is client-side only (no server-side blocklist). Stolen tokens remain valid until expiry.
- No map library integrated for location picking — number-input fallback only unless time permits.
