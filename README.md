# fullstack-fastapi-sveltekit

A [copier](https://github.com/copier-org/copier) template for a production-ready fullstack web application.

## Stack

- **Backend**: FastAPI + SQLAlchemy + Alembic (Python 3.13+) + SQLite
- **Frontend**: SvelteKit 2 + Svelte 5 + TypeScript + Tailwind CSS 4
- **Auth**: OIDC via Keycloak (preloaded dev realm)
- **Infra**: Docker Compose + Traefik + optional S3 storage + OpenTelemetry

## Usage

```bash
uvx copier copy gh:gmolveau/cookiecutter-fastapi-svelte ./my-project
```

Follow the prompts:

- `project_name` - Human-readable project name (e.g. `My App`)
- `project_slug` - URL and Docker image name (e.g. `my-app`)
- `python_package_name` - Python package identifier (e.g. `myapp`)
- `description` - Short app description
- `author_name` - Your name
- `github_username` - GitHub username (for image registry)

## Test it quickly

```bash
uvx copier copy gh:gmolveau/cookiecutter-fastapi-svelte /tmp/test-app \
  --data project_name="Test App" \
  --data project_slug="test-app" \
  --data python_package_name="testapp" \
  --data description="Testing the template" \
  --defaults
```

## Update a generated project

Because copier saves answers in `.copier-answers.yml`, you can pull template updates into an existing project:

```bash
cd my-project
uvx copier update
```

## Developers

### Run the template

Instantiate the template by using :

```bash
uvx copier copy . ./app \
  --trust \
  --data project_name="MyApp" \
  --data project_slug="my-app" \
  --data python_package_name="myapp" \
  --data description="My app from template" \
  --defaults
```

This will create the `app`, then run it :

```bash
cd app
just dev-up
```

### Backport changes from app to template

After editing files in `app/`, use the interactive backport script to propagate changes back into `template/`:

```bash
uv run scripts/backport.py
```

The script:

- Detects files that differ between `template/` (rendered with your copier variables) and `app/`
- Detects files deleted from `app/` that still exist in `template/`
- For **changed** files: shows a unified diff and asks whether to backport (app → template, with values re-replaced by their `[[ var ]]` placeholders) ;
- For **new** files ;
- For **deleted** files: asks whether to remove the file from `template/`

### Test it locally

```bash
uvx copier copy ~/dev/cookiecutter-fastapi-svelte /tmp/test-app \
  --data project_name="Test App" \
  --data project_slug="test-app" \
  --data python_package_name="testapp" \
  --data description="Testing the template" \
  --defaults

just dev-up
# go to http://app.localhost
```
