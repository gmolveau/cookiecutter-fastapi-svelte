FROM node:trixie-slim@sha256:46c2e03fa9f715d1568ebf054e27d2cf74d4c0897f2ad1763ae571d27190dfdd AS base

SHELL ["/bin/bash", "-c"]

FROM base AS dev_base

COPY --from=ghcr.io/casey/just:latest@sha256:60c0e2abbf221ee0a8ea9a5057160a30a4a7f1c1603bd3bf35c8aea01401d357 /just /usr/local/bin/

RUN npm install -g pnpm@latest-10

ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"

COPY . /app
WORKDIR /app

FROM dev_base AS dev
RUN --mount=type=cache,id=pnpm,target=/pnpm/store just install-dev
EXPOSE 5173
CMD [ "just", "run-dev" ]

FROM dev_base AS build-prod
ARG APP_VERSION=dev
ENV APP_VERSION=$APP_VERSION
RUN --mount=type=cache,id=pnpm,target=/pnpm/store just install-prod && just build

FROM base AS prod
WORKDIR /app
COPY --from=build-prod /app/node_modules /app/node_modules
COPY --from=build-prod /app/build /app/build
COPY --from=build-prod /app/package.json /app/package.json
EXPOSE 3000
CMD [ "node", "-r", "dotenv/config", "build" ]
