# fullstack-fastapi-sveltekit

A [cookiecutter](https://github.com/cookiecutter/cookiecutter) template for a production-ready fullstack web application.

## Stack

- **Backend**: FastAPI + SQLAlchemy + Alembic (Python 3.13+) + SQLite
- **Frontend**: SvelteKit 2 + Svelte 5 + TypeScript + Tailwind CSS 4
- **Auth**: OIDC via Keycloak (preloaded dev realm)
- **Infra**: Docker Compose + Traefik + optional S3 storage + OpenTelemetry

## Usage

```bash
uvx cookiecutter gh:gmolveau/cookiecutter-fastapi-svelte
```

Follow the prompts:

| Variable              | Description                          | Example     |
| --------------------- | ------------------------------------ | ----------- |
| `project_name`        | Human-readable project name          | `My App`    |
| `project_slug`        | URL and Docker image name            | `my-app`    |
| `python_package_name` | Python package identifier            | `myapp`     |
| `description`         | Short app description                | `A web app` |
| `author_name`         | Your name                            | `Jane Doe`  |
| `github_username`     | GitHub username (for image registry) | `janedoe`   |

## Test it quickly

```bash
cd /tmp && mkdir ttt & cd ttt && \
uvx cookiecutter gh:gmolveau/cookiecutter-fastapi-svelte \
  --no-input \
  project_name="Test App" \
  project_slug="test-app" \
  python_package_name="testapp" \
  description="Testing the template"
```
