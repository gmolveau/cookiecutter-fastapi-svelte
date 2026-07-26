# Developer Guide

## The app

MyApp — MyApp

A fullstack web application with a FastAPI backend and SvelteKit frontend. Authentication is handled via Keycloak (OIDC).

---

## Repo layout

```console
MyApp/
├── backend/          # Python / FastAPI API
├── frontend/         # SvelteKit SPA
├── keycloak/         # Keycloak realm export for local dev
├── docs/             # This documentation
│   ├── dev.md        # ← you are here
│   ├── env.md        # All environment variables and defaults
│   └── adr/          # Architecture decision records
├── compose.yml            # Docker Compose dev stack
├── compose.localprod.yml  # Docker Compose local-prod stack
├── justfile               # Top-level convenience targets
├── .env.dev.example       # Example env file for development
└── .env.prod.example      # Example env file for production
```

---

## Getting started

### Prerequisites

| Tool          | Purpose                | Install                                                     |
| ------------- | ---------------------- | ----------------------------------------------------------- |
| Python ≥ 3.13 | Backend runtime        | [python.org](https://python.org)                            |
| `uv`          | Python package manager | `curl -LsSf https://astral.sh/uv/install.sh \| sh`          |
| Node.js ≥ 20  | Frontend runtime       | [nodejs.org](https://nodejs.org)                            |
| `pnpm`        | Node package manager   | [pnpm.io/installation](https://pnpm.io/installation)        |
| `just`        | Task runner            | `brew install just` / [docs](https://github.com/casey/just) |

### First-time setup

```bash
# Init the env files (create symbolic links in frontend/backend)
just init-env

# Install all dependencies (backend + frontend)
just install-dev

# Create and apply the initial DB migration
cd backend && just new-migrate name=initial && just migrate
```

See [`docs/env.md`](env.md) for every available variable and its default value.

### Running locally

#### With Docker Compose

```bash
just dev-up
```

The app is available at <http://app.localhost>.

Interactive API docs: <http://app.localhost/api/docs>.

Keycloak: <http://keycloak.localhost>.

Jaeger UI (traces): <http://jaeger.localhost>.

#### Without Docker Compose

Edit the Keycloak URL in `.env` and uncomment the variables with "without docker compose".

Open 3 terminals.

**Backend** (port 8000)

```bash
cd backend
just migrate       # apply pending DB migrations (first run + after pulling changes)
just run-dev       # uvicorn with --reload
```

**Frontend** (port 5173)

```bash
cd frontend
just run-dev       # Vite dev server
```

**Keycloak** (port 8080)

```bash
just run-keycloak  # ephemeral Keycloak container
```

The app is available at <http://localhost:5173>.

Interactive API docs: <http://localhost:8000/api/docs>.

Keycloak admin: <http://localhost:8080> (user: `keycloak` / password: `keycloak`).

#### Authentication

Keycloak is preloaded with 2 users:

- `user:user` in the group `developers`
- `admin:admin` in the group `sysadmins`

Use the CLI to give the superadmin role to the admin user:

```bash
uv run manage.py users make-superadmin --email "admin@example.com"
```

## Architecture overview

```console
Browser
  │  HTTP (REST JSON)
  ▼
FastAPI  ──────  SQLite (SQLAlchemy / Alembic)
  │
  ├──  Storage disk  ──  Local FS  (default)
  │                 └──  AWS S3 / S3-compatible  (optional)
  │
  └──  OpenTelemetry (optional)  ──  Jaeger (OTLP/HTTP :4318)
```

The frontend is a **pure client-side SPA** — all data comes from the backend API.

---

## Backend

### Stack

| Library            | Role                                             |
| ------------------ | ------------------------------------------------ |
| FastAPI            | HTTP framework, request validation, OpenAPI docs |
| SQLAlchemy 2 (ORM) | Database access                                  |
| Alembic            | Schema migrations                                |
| Pydantic           | Request / response schemas                       |
| boto3              | S3 storage driver                                |
| uv                 | Package and virtual-env management               |
| ruff               | Linter + formatter                               |
| ty                 | Static type checker                              |
| bandit             | Security linter                                  |

### Source layout

```console
backend/src/
├── web.py               # App factory: CORS, middleware, router registration
├── config.py            # Settings loaded from environment via Pydantic
├── otel_setup.py        # OpenTelemetry tracer provider + instrumentation
├── database.py          # Engine, session factory, get_db() dependency
├── dependencies.py      # Shared FastAPI dependencies (auth, current user)
├── models.py            # SQLAlchemy ORM models (User, Group, Role, Project)
├── exceptions.py        # Domain exceptions
├── migrations/          # Alembic env + versioned migration scripts
├── schemas/
├── services/
│   └── users.py         # Business logic for users (upsert on login)
├── routes/
│   ├── auth.py          # OAuth2 / Keycloak login, callback, logout, /auth/me
│   ├── health.py        # GET /health
├── storage/
│   ├── disk.py          # StorageDisk abstract base class
│   ├── local.py         # LocalDisk implementation (dev default)
│   └── s3.py            # S3Disk implementation
└── cli/
    ├── main.py          # CLI entry point (click app)
    └── users.py         # CLI commands for user management
```

### Data model

| Model   | Key fields                                       |
| ------- | ------------------------------------------------ |
| `User`  | `name`, `email`, `sub` (OIDC subject), `role_id` |
| `Role`  | `name`                                           |
| `Group` | `name`, `role_id`; many-to-many with `User`      |

### Request lifecycle

```console
Route handler (src/routes/)
  → calls service function (src/services/)
     → queries DB via SQLAlchemy session
  → builds Pydantic response schema
  → returns JSON
```

Route handlers are intentionally thin — no business logic. Keep domain rules in `services/`.

### Auth flow

Login uses the OAuth2 authorization code flow via Keycloak:

1. Frontend redirects to `GET /api/auth/login?next=<url>`
2. Backend redirects to Keycloak authorization endpoint
3. Keycloak redirects back to `GET /api/auth/callback`
4. Backend exchanges code for tokens, upserts the user in the DB, stores user ID in a signed session cookie
5. Backend redirects to `next`

### Storage abstraction

`StorageDisk` exposes four methods: `save`, `delete`, `url`, `ensure`. The active implementation is selected at startup from `STORAGE_DRIVER` and exposed as a FastAPI dependency via `get_disk()`. Add a new driver by subclassing `StorageDisk` and registering it in `storage/__init__.py`.

### Observability (OpenTelemetry + Jaeger)

Set the following variables in your `.env` to enable tracing:

```env
OTEL_ENABLED=true
OTEL_SERVICE_NAME=MyApp
OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4318
```

Open the Jaeger UI at <http://jaeger.localhost> and search traces by service name.

### Database migrations

```bash
cd backend
# After editing a model, generate a migration
just new-migrate name=describe_your_change

# Apply all pending migrations
just migrate

# Check that models and DB are in sync (runs in CI)
just alembic-check
```

---

## Frontend

### Stack

| Tool                   | Role                    |
| ---------------------- | ----------------------- |
| SvelteKit 2 + Svelte 5 | Framework and routing   |
| TypeScript (strict)    | Type safety             |
| Tailwind CSS 4         | Utility-first styling   |
| Vite                   | Build tool / dev server |
| pnpm                   | Package manager         |

### Source layout

```console
frontend/src/
├── lib/
│   ├── api/
│   │   ├── auth.ts       # Auth API calls (login URL, logout, getMe)
│   │   ├── client.ts     # Base fetch wrapper
│   │   └── items.ts      # Item CRUD API calls
│   ├── types/
│   │   └── index.ts      # Shared TypeScript interfaces
│   ├── stores/
│   │   └── auth.svelte.ts  # Auth store: tri-state undefined/null/User
│   └── components/
│       ├── AppHeader.svelte     # Shared header with auth state
│       └── PaginationBar.svelte # Reusable pagination component
└── routes/
    ├── +layout.svelte    # Root layout — imports Tailwind, initialises auth
    ├── +page.svelte      # / — home page
    └── items/
        └── +page.svelte  # /items — item list
```

### Auth store

`auth.svelte.ts` exposes a tri-state `auth.user`:

- `undefined` — initial state, `/auth/me` not yet called (shows loading)
- `null` — user is not logged in
- `User` — user is authenticated

`auth.init()` is called once in the root layout.

### Checks and formatting

```bash
cd frontend
just format    # Prettier
just checks    # ESLint
```

---

## just targets (quick reference)

| Directory   | Target                    | What it does                                |
| ----------- | ------------------------- | ------------------------------------------- |
| root        | `just install-dev`        | Install backend + frontend dependencies     |
| root        | `just format`             | Format all code                             |
| root        | `just dev-up`             | Start full stack via Docker Compose         |
| root        | `just run-keycloak`       | Start ephemeral Keycloak container          |
| `backend/`  | `just run-dev`            | Start API server with hot reload            |
| `backend/`  | `just migrate`            | Apply pending DB migrations                 |
| `backend/`  | `just new-migrate name=x` | Generate a new migration from model changes |
| `backend/`  | `just checks`             | ty + ruff + bandit                          |
| `frontend/` | `just run-dev`            | Start Vite dev server                       |
| `frontend/` | `just checks`             | ESLint                                      |
