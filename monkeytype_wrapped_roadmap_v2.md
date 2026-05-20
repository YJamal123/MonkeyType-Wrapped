# MonkeyType Analytics — Development Roadmap v2
### Optimized for 2027 SWE New Grad Roles

## Resume Framing
> **"AI-powered typing analytics platform"** — not just "a web app"

## Tech Stack
| Layer | Technology | Resume Signal |
|---|---|---|
| Backend | Python + FastAPI | #1 most demanded language in 2026 job postings |
| Database | PostgreSQL + SQLAlchemy | Universal — appears in nearly every JD |
| Caching | Redis | Production-grade, not toy-level |
| Frontend | React + TypeScript | TS increasingly required in job postings |
| AI Feature | Anthropic API (claude-sonnet) | Biggest differentiator for 2027 |
| Containerization | Docker + Docker Compose | Entry point to cloud-native / DevOps |
| CI/CD | GitHub Actions | Shows production engineering mindset |
| Deployment | Railway (backend) + Vercel (frontend) | Shows you can ship end-to-end |

---

## Milestone 1 — Project Setup & Infrastructure

### 1.1 Repository Structure
```
monkeytype-analytics/
├── backend/
│   ├── main.py
│   ├── routers/
│   │   ├── results.py
│   │   ├── stats.py
│   │   ├── activity.py
│   │   ├── leaderboard.py
│   │   └── insights.py          # AI endpoint
│   ├── services/
│   │   ├── monkeytype.py        # MonkeyType API client
│   │   ├── cache.py             # Redis caching layer
│   │   ├── analytics.py         # pandas processing logic
│   │   └── ai_insights.py       # Anthropic API integration
│   ├── models/
│   │   └── schemas.py           # Pydantic schemas
│   ├── db/
│   │   ├── database.py          # SQLAlchemy setup
│   │   └── models.py            # DB table definitions
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── api/
│   │   └── types/               # TypeScript interfaces
│   ├── package.json
│   ├── tsconfig.json
│   └── .env
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions pipeline
├── docker-compose.yml
└── README.md
```

### 1.2 Docker & Docker Compose
- Write a `Dockerfile` for the FastAPI backend (Python 3.12 slim image)
- Write a `docker-compose.yml` that spins up three services:
  - `backend` — FastAPI app
  - `postgres` — PostgreSQL 16
  - `redis` — Redis 7
- This means the entire backend stack starts with a single `docker compose up` command

### 1.3 Backend: FastAPI App
- Initialize FastAPI app in `main.py` with lifespan context manager
- Install dependencies: `fastapi`, `uvicorn`, `httpx`, `python-dotenv`, `pandas`, `sqlalchemy`, `asyncpg`, `redis[asyncio]`, `anthropic`
- Load all secrets from `.env`: `APE_KEY`, `DATABASE_URL`, `REDIS_URL`, `ANTHROPIC_API_KEY`
- Configure CORS middleware for `http://localhost:5173`
- Register all routers with `/api` prefix
- Health check endpoint `GET /health` returning service status for all three services (API, DB, Redis)

### 1.4 PostgreSQL Database
- Set up SQLAlchemy async engine with `asyncpg`
- Create an `alembic` migration setup for schema versioning
- Define two tables:
  - `results_cache` — stores fetched MonkeyType results with `user_id`, `fetched_at`, `data` (JSONB)
  - `ai_insights` — stores generated AI insights with `user_id`, `prompt_hash`, `insight`, `created_at`
- This prevents re-fetching and re-generating on every request

### 1.5 Redis Caching Layer
- Create `services/cache.py` using `redis.asyncio`
- Cache strategy:
  - `/results` → TTL 6 hours (rate limit is 30 req/day)
  - `/users/personalBests` → TTL 1 hour
  - `/users/currentTestActivity` → TTL 1 hour
  - `/public/speedHistogram` → TTL 24 hours (public data, rarely changes)
- Always check Redis before PostgreSQL before MonkeyType API (cache waterfall)

### 1.6 MonkeyType API Service
- Create `services/monkeytype.py` using `httpx.AsyncClient`
- Attach `Authorization: ApeKey {APE_KEY}` header to all authenticated requests
- Base URL: `https://api.monkeytype.com`
- Wrap every call with the cache waterfall from 1.5

### 1.7 Frontend: React + TypeScript App
- Scaffold with Vite: `npm create vite@latest frontend -- --template react-ts`
- Install dependencies: `axios`, `recharts`, `react-calendar-heatmap`, `tailwindcss`, `@types/react-calendar-heatmap`
- Configure Tailwind CSS
- Create `.env` with `VITE_API_URL=http://localhost:8000`
- Create `src/types/` folder with TypeScript interfaces matching all backend Pydantic schemas
- Create `src/api/client.ts` — typed axios instance

---

## Milestone 2 — WPM Growth Over Time

### 2.1 Backend
- `GET /api/results` endpoint in `routers/results.py`
- Fetch from MonkeyType `GET /results` (via cache waterfall)
- Use pandas to sort by timestamp ascending
- Return typed array: `{ timestamp: int, date: str, wpm: float, rawWpm: float, language: str, mode: str, mode2: str }`
- Support optional query params: `mode`, `mode2`, `language` for filtering

### 2.2 Frontend
- TypeScript interface `Result` matching the response shape
- `WpmChart` component using Recharts `LineChart`
- X-axis: formatted date string
- Y-axis: WPM
- Two lines: raw WPM per test + rolling 10-test average
- Filter bar: mode (time/words), mode2 (15/30/60/120)
- Stat cards above chart: earliest avg WPM, latest avg WPM, delta with colored arrow

---

## Milestone 3 — Accuracy & Consistency Trends

### 3.1 Backend
- `GET /api/stats/summary` endpoint in `routers/stats.py`
- Uses cached results data — no new MonkeyType API call
- pandas computes:
  - Early 20% vs. late 20% averages for WPM, accuracy, consistency
  - Overall mean and standard deviation for each metric
- Return structured summary object

### 3.2 Frontend
- `AccuracyChart` — line chart of accuracy over time with rolling average
- `ConsistencyChart` — line chart of consistency over time
- Summary stat cards with early vs. late comparison
- All components accept the same `Result[]` data already fetched in Milestone 2 (no extra API calls)

---

## Milestone 4 — Personal Bests by Mode

### 4.1 Backend
- `GET /api/personal-bests` endpoint
- Fetches from MonkeyType `GET /users/personalBests?mode={mode}`
- Returns PB data grouped by mode2 with full stat breakdown

### 4.2 Frontend
- TypeScript interface `PersonalBest` for the response
- `PersonalBests` component with tab selector for mode
- Cards per mode2 value showing: WPM, raw WPM, accuracy, consistency, date achieved

---

## Milestone 5 — Test Activity Heatmap

### 5.1 Backend
- `GET /api/activity` endpoint
- Fetches from MonkeyType `GET /users/currentTestActivity`
- Converts `testsByDays` array + `lastDay` timestamp into `{ date: str, count: int }[]`

### 5.2 Frontend
- `ActivityHeatmap` component using `react-calendar-heatmap`
- GitHub-style calendar grid showing tests per day
- Hover tooltip with date and count
- Stat row below: current streak, max streak, total tests, most active day

---

## Milestone 6 — Community Comparison (Speed Histogram)

### 6.1 Backend
- `GET /api/community/histogram` endpoint
- Fetches from MonkeyType `GET /public/speedHistogram` (public, no auth needed)
- Params: `language` (default `english`), `mode` (default `time`), `mode2` (default `60`)
- Fetches user's PB for same mode from cached personal bests
- Returns: histogram buckets + user's PB wpm + calculated percentile

### 6.2 Frontend
- `SpeedHistogram` component using Recharts `BarChart`
- WPM distribution as bars across the X-axis
- User's PB highlighted as a distinct color with a label
- Percentile badge: "You're faster than X% of players"
- Dropdown controls for language, mode, mode2

---

## Milestone 7 — Language Breakdown

### 7.1 Backend
- `GET /api/stats/languages` endpoint
- Reuses cached results — no new MonkeyType call
- pandas `groupby('language')['wpm'].agg(['count', 'mean', 'max'])`
- Returns sorted list of `{ language, testCount, avgWpm, maxWpm }`

### 7.2 Frontend
- `LanguageBreakdown` component
- Horizontal bar chart sorted by avgWpm
- Highlight most-used language and highest-avg language in different colors
- Only show languages with 3+ tests to avoid single-test noise

---

## Milestone 8 — AI Insights (Key Differentiator)

This is the feature that transforms the resume bullet from "built a dashboard" to "built an AI-powered analytics platform."

### 8.1 Backend
- Install `anthropic` Python SDK
- Create `services/ai_insights.py`
- `GET /api/insights` endpoint in `routers/insights.py`
- Logic:
  1. Pull the user's full stats summary (WPM growth, accuracy trend, language breakdown, streak data)
  2. Check PostgreSQL `ai_insights` table — if a recent insight exists (< 24h), return it
  3. Otherwise, construct a prompt with the user's stats and call `claude-sonnet-4-6`
  4. Store the result in PostgreSQL with a timestamp
  5. Return the insight text
- Example prompt structure:
  ```
  You are a typing performance coach. Analyze this user's MonkeyType statistics
  and provide 3-4 specific, actionable insights about their performance trends.
  Be specific with numbers. Keep each insight to 1-2 sentences.

  Stats:
  - Early avg WPM: {early_wpm} → Late avg WPM: {late_wpm} ({delta:+.1f} change)
  - Accuracy trend: {early_acc}% → {late_acc}%
  - Most-used language: {top_language} ({top_count} tests)
  - Current streak: {streak} days
  - Best mode: {best_mode} at {best_wpm} WPM
  ...
  ```

### 8.2 Frontend
- `AIInsights` component — prominent card on the dashboard
- Displays 3-4 bullet insights with a "Regenerate" button (rate limited)
- Show "Generated with Claude" attribution and timestamp
- Loading skeleton with animated typing cursor (thematic!)

---

## Milestone 9 — Dashboard Layout & Polish

### 9.1 Layout
- Main `Dashboard` page composing all components
- Sticky top nav with section links
- Responsive grid layout (2-col on desktop, 1-col on mobile)
- Loading skeletons for every component while data fetches
- Global error boundary with friendly error states

### 9.2 Design Direction
- Dark theme matching MonkeyType's aesthetic (dark gray / near-black background)
- Monospaced font (JetBrains Mono or Fira Code) for all stat numbers
- Accent color pulled from MonkeyType's yellow (`#e2b714`)
- Smooth Recharts animations on mount
- Green/red color coding for positive/negative trends

### 9.3 TypeScript Strictness
- Enable `strict: true` in `tsconfig.json`
- No `any` types — every API response should have a matching interface in `src/types/`
- This is a talking point in interviews: "I enforced strict TypeScript throughout"

---

## Milestone 10 — CI/CD Pipeline (GitHub Actions)

### 10.1 CI Pipeline (`.github/workflows/ci.yml`)
Runs on every push and pull request to `main`:
- **Backend job:**
  - Spin up PostgreSQL and Redis as GitHub Actions services
  - Install Python dependencies
  - Run `pytest` on at least 3 backend tests (health check, results endpoint, cache hit/miss)
- **Frontend job:**
  - Install Node dependencies
  - Run `tsc --noEmit` (TypeScript type check — zero errors required)
  - Run `npm run build` (must succeed)

### 10.2 CD Pipeline
- On merge to `main`, automatically deploy:
  - Backend → Railway (connect GitHub repo, auto-deploy on push)
  - Frontend → Vercel (connect GitHub repo, auto-deploy on push)

---

## Milestone 11 — Deployment & Production Hardening

### 11.1 Backend (Railway)
- Add `railway.json` or use Dockerfile deploy
- Set environment variables in Railway dashboard: `APE_KEY`, `DATABASE_URL`, `REDIS_URL`, `ANTHROPIC_API_KEY`
- Railway provides managed PostgreSQL and Redis add-ons — use them
- Update CORS to allow your production Vercel domain

### 11.2 Frontend (Vercel)
- Connect GitHub repo to Vercel
- Set `VITE_API_URL` to your Railway backend URL
- Vercel auto-deploys on every push to `main`

### 11.3 README (Don't Skip This)
A strong README is part of the project for resume purposes. Include:
- Project description with the "AI-powered" framing
- Architecture diagram (can be a simple ASCII diagram)
- Full tech stack table
- Local development instructions using `docker compose up`
- Link to live demo
- Screenshots of the dashboard

---

## Key Technical Notes for Claude Code

1. **Never expose the ApeKey or Anthropic API key in the frontend.** All external API calls go through the FastAPI backend only.
2. **Cache waterfall order:** Redis → PostgreSQL → MonkeyType API. Always check in this order.
3. **Timestamps from MonkeyType are in milliseconds** — use `pd.to_datetime(ts, unit='ms')` or divide by 1000.
4. **The `/results` endpoint returns at most 1000 results** — use `onOrAfterTimestamp` to paginate if needed.
5. **`/public/speedHistogram` requires `language`, `mode`, and `mode2` params** — default to `english`, `time`, `60`.
6. **Use `httpx.AsyncClient` in FastAPI** (not `requests`) to keep all endpoints non-blocking.
7. **SQLAlchemy async sessions** must use `async with AsyncSession() as session` — never use sync session in async context.
8. **AI insights should be cached in PostgreSQL** — the Anthropic API is not free and calling it on every page load would be costly.
9. **TypeScript strict mode is on** — every component prop and API response must be typed. No `any`.
10. **Write at least one pytest test per router** before Milestone 10 — don't leave testing until the end.

---

## Resume Bullet Points (Use These)

Once shipped, frame it like this on your resume:

> **MonkeyType Analytics** | Python, FastAPI, PostgreSQL, Redis, React, TypeScript, Docker, GitHub Actions
> - Built an AI-powered typing analytics platform integrating the MonkeyType API, processing 1,000+ test results with pandas to surface WPM growth trends, accuracy analysis, and community percentile rankings
> - Architected a Redis + PostgreSQL cache waterfall reducing MonkeyType API calls by ~95%, working within a 30 req/day rate limit
> - Integrated the Anthropic Claude API to generate personalized performance insights, storing results in PostgreSQL to minimize API costs
> - Containerized the full stack with Docker Compose and implemented a CI/CD pipeline using GitHub Actions with automated TypeScript type-checking and pytest test suite
> - Deployed backend to Railway and frontend to Vercel with environment-based configuration and automatic deploys on merge to main
