FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim@sha256:82f018bb3bd8b1d12c376c3e87da186ec1932cbf91bc8e73089feea6428fec00 AS base

SHELL ["/bin/bash", "-c"]

COPY --from=ghcr.io/casey/just:latest@sha256:60c0e2abbf221ee0a8ea9a5057160a30a4a7f1c1603bd3bf35c8aea01401d357 /just /usr/local/bin/

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

FROM base AS dev

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=justfile,target=justfile \
    just install-dev

COPY . /app

RUN --mount=type=cache,target=/root/.cache/uv \
    just install-dev

EXPOSE 8000

CMD ["just", "run-dev"]

FROM base AS prod

ARG APP_VERSION
ENV APP_VERSION=$APP_VERSION

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=justfile,target=justfile \
    just install

COPY . /app

RUN --mount=type=cache,target=/root/.cache/uv \
    just install

EXPOSE 8000

CMD ["just", "run-prod"]
