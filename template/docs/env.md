# Environment Variables

## Frontend

Configured via a `.env` file at `frontend/`.
Variables must be prefixed with `VITE_` to be exposed to the browser (SvelteKit / Vite convention).

- `PUBLIC_API_URL` — Base URL of the backend API. Used to build all API and image URLs. *(default: `http://localhost:8000`)*
- `PUBLIC_BASE_URL` — Public URL of the frontend. Used to build the post-login redirect. *(default: `http://localhost:5173`)*

---

## Backend

Configured via a `.env` file at the repo root (e.g. copy `.env.dev.example`).

### Security / CORS

- `ALLOWED_HOSTS` — Comma-separated list of allowed `Host` header values (`TrustedHostMiddleware`).
- `ALLOWED_ORIGINS` — Comma-separated list of origins allowed by CORS.

### Authentication (Keycloak / OIDC)

- `OIDC_CLIENT_ID` (**required**) — OAuth2 client ID registered in Keycloak.
- `OIDC_CLIENT_SECRET` (**required**) — OAuth2 client secret.
- `OIDC_AUTHORIZE_URL` (**required**) — Keycloak authorization endpoint URL.
- `OIDC_ACCESS_TOKEN_URL` (**required**) — Keycloak token endpoint URL.
- `OIDC_JWT_URL` (**required**) — Keycloak JWKS endpoint URL (for token validation).
- `OIDC_REQUIRE_EMAIL_VERIFIED` — Reject login if the OIDC provider reports the email as unverified. Set to `false` when using a provider that does not issue `email_verified`, or in local dev. *(default: `true`)*

### Session

- `SESSION_SECRET_KEY` (**required**) — Secret used to sign the session cookie (use a random string).
- `SESSION_COOKIE_MAX_AGE` (**required**) — Session cookie lifetime in seconds (e.g. `86400` = 24 h).

### Environment

- `APP_ENV` — Runtime environment. Accepted values: `dev`, `prod`, `test`. Affects security behaviour (e.g. cross-origin login redirects are only allowed in `dev`). *(default: `dev`)*

### Rate Limiting

- `RATE_LIMIT` — Global rate limit applied to all endpoints. Format: `N/second|minute|hour|day`. *(default: `60/minute`)*

### Database

- `DATABASE_URL` — SQLAlchemy connection URL. *(default: `sqlite:///./data/sqlite.db`)*

### Logging

- `LOG_LEVEL` — Minimum log level. Accepted values: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. *(default: `INFO`)*

### OpenTelemetry

- `OTEL_ENABLED` — Set to `true` to enable OpenTelemetry tracing. *(default: `false`)*
- `OTEL_SERVICE_NAME` — Service name reported in traces. *(default: `[[ project_name ]]`)*
- `OTEL_EXPORTER_OTLP_ENDPOINT` — Base URL of the OTLP HTTP collector (e.g. `http://jaeger:4318`). Traces are sent to `<endpoint>/v1/traces`.

### Storage

- `STORAGE_DRIVER` — Storage backend to use. Accepted values: `local`, `s3`. *(default: `local`)*

#### Local driver (`STORAGE_DRIVER=local`)

- `STORAGE_LOCAL_PATH` — Directory path for the files.

#### S3 driver (`STORAGE_DRIVER=s3`)

- `STORAGE_S3_BUCKET` (**required**) — S3 bucket name.
- `STORAGE_S3_REGION` — AWS region (or equivalent for S3-compatible services). *(default: `us-east-1`)*
- `STORAGE_S3_PREFIX` — Key prefix inside the bucket.
- `STORAGE_S3_ENDPOINT_URL` — Custom endpoint URL for S3-compatible services (MinIO, Cloudflare R2, …). Omit for AWS.
- `STORAGE_S3_ACCESS_KEY_ID` — Explicit AWS / S3-compatible access key. Can be omitted when using IAM roles.
- `STORAGE_S3_SECRET_ACCESS_KEY` — Explicit AWS / S3-compatible secret key. Can be omitted when using IAM roles.

---

## Docker

- `APP_VERSION` - The version of the app (git tag ; eg `0.1.0`).
- `DATA_VOLUME` - The data volume name (eg: `app_data`) or data volume path if binded volume is wanted (eg: `./data`)
