# Environment Variables

## Frontend

Configured via a `.env` file at `frontend/`.
Variables must be prefixed with `VITE_` to be exposed to the browser (SvelteKit / Vite convention).

| Variable          | Default                 | Description                                                        |
| ----------------- | ----------------------- | ------------------------------------------------------------------ |
| `PUBLIC_API_URL`  | `http://localhost:8000` | Base URL of the backend API. Used to build all API and image URLs. |
| `PUBLIC_BASE_URL` | `http://localhost:5173` | Public URL of the frontend. Used to build the post-login redirect. |

---

## Backend

Configured via a `.env` file at the repo root (e.g. copy `.env.dev.example`).

### Security / CORS

| Variable          | Default | Description                                                                     |
| ----------------- | ------- | ------------------------------------------------------------------------------- |
| `ALLOWED_HOSTS`   | —       | Comma-separated list of allowed `Host` header values (`TrustedHostMiddleware`). |
| `ALLOWED_ORIGINS` | —       | Comma-separated list of origins allowed by CORS.                                |

### Authentication (Keycloak / OIDC)

| Variable                    | Default | Required | Description                                        |
| --------------------------- | ------- | -------- | -------------------------------------------------- |
| `KEYCLOAK_CLIENT_ID`        | —       | **Yes**  | OAuth2 client ID registered in Keycloak.           |
| `KEYCLOAK_CLIENT_SECRET`    | —       | **Yes**  | OAuth2 client secret.                              |
| `KEYCLOAK_AUTHORIZE_URL`    | —       | **Yes**  | Keycloak authorization endpoint URL.               |
| `KEYCLOAK_ACCESS_TOKEN_URL` | —       | **Yes**  | Keycloak token endpoint URL.                       |
| `KEYCLOAK_JWT_URL`          | —       | **Yes**  | Keycloak JWKS endpoint URL (for token validation). |

### Session

| Variable                 | Default | Required | Description                                                   |
| ------------------------ | ------- | -------- | ------------------------------------------------------------- |
| `SESSION_SECRET_KEY`     | —       | **Yes**  | Secret used to sign the session cookie (use a random string). |
| `SESSION_COOKIE_MAX_AGE` | —       | **Yes**  | Session cookie lifetime in seconds (e.g. `86400` = 24 h).     |

### Environment

| Variable  | Default | Description                                                                                                                                            |
| --------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `APP_ENV` | `dev`   | Runtime environment. Accepted values: `dev`, `prod`, `test`. Affects security behaviour (e.g. cross-origin login redirects are only allowed in `dev`). |

### Rate Limiting

| Variable     | Default     | Description                                                                        |
| ------------ | ----------- | ---------------------------------------------------------------------------------- |
| `RATE_LIMIT` | `60/minute` | Global rate limit applied to all endpoints. Format: `N/second\|minute\|hour\|day`. |

### Database

| Variable       | Default                              | Description                                                 |
| -------------- | ------------------------------------ | ----------------------------------------------------------- |
| `DATABASE_URL` | `sqlite:///./data/meme_generator.db` | SQLAlchemy connection URL. Defaults to a local SQLite file. |

### Logging

| Variable    | Default | Description                                                                          |
| ----------- | ------- | ------------------------------------------------------------------------------------ |
| `LOG_LEVEL` | `INFO`  | Minimum log level. Accepted values: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. |

### OpenTelemetry

| Variable                      | Default         | Required | Description                                                                                                 |
| ----------------------------- | --------------- | -------- | ----------------------------------------------------------------------------------------------------------- |
| `OTEL_ENABLED`                | `false`         | No       | Set to `true` to enable OpenTelemetry tracing.                                                              |
| `OTEL_SERVICE_NAME`           | `memegenerator` | No       | Service name reported in traces.                                                                            |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | —               | No       | Base URL of the OTLP HTTP collector (e.g. `http://jaeger:4318`). Traces are sent to `<endpoint>/v1/traces`. |

### Storage

| Variable         | Default | Description                                             |
| ---------------- | ------- | ------------------------------------------------------- |
| `STORAGE_DRIVER` | `local` | Storage backend to use. Accepted values: `local`, `s3`. |

#### Local driver (`STORAGE_DRIVER=local`)

| Variable                 | Default             | Description                                                     |
| ------------------------ | ------------------- | --------------------------------------------------------------- |
| `STORAGE_LOCAL_PATH`     | `static/templates`  | Filesystem directory where uploaded template images are stored. |
| `STORAGE_LOCAL_BASE_URL` | `/static/templates` | URL prefix used to build public image URLs.                     |

#### S3 driver (`STORAGE_DRIVER=s3`)

| Variable                       | Default      | Required | Description                                                                             |
| ------------------------------ | ------------ | -------- | --------------------------------------------------------------------------------------- |
| `STORAGE_S3_BUCKET`            | —            | **Yes**  | S3 bucket name.                                                                         |
| `STORAGE_S3_REGION`            | `us-east-1`  | No       | AWS region (or equivalent for S3-compatible services).                                  |
| `STORAGE_S3_PREFIX`            | `templates/` | No       | Key prefix inside the bucket.                                                           |
| `STORAGE_S3_ENDPOINT_URL`      | —            | No       | Custom endpoint URL for S3-compatible services (MinIO, Cloudflare R2, …). Omit for AWS. |
| `STORAGE_S3_ACCESS_KEY_ID`     | —            | No       | Explicit AWS / S3-compatible access key. Can be omitted when using IAM roles.           |
| `STORAGE_S3_SECRET_ACCESS_KEY` | —            | No       | Explicit AWS / S3-compatible secret key. Can be omitted when using IAM roles.           |
