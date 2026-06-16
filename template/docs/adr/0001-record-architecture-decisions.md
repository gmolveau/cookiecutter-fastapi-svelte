# 1. Record architecture decisions

Date: 2026-06-16

## Status

Accepted

## Context

We need to record the architectural decisions made on this project so that the
reasoning behind them is preserved for future contributors (human and agent).
Decisions are easy to make and hard to remember; without a record, the *why*
behind a design is lost and gets relitigated.

## Decision

We will use Architecture Decision Records, as
[described by Michael Nygard](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions).

Records live in `docs/adr/`, are written in Markdown, numbered sequentially,
and are immutable once accepted. A superseded decision is replaced by a new
record rather than edited in place.

## Consequences

- The history and rationale of decisions is discoverable in the repo.
- Each non-trivial architectural change carries the small cost of writing a
  record.
- See `docs/adr/README.md` for the authoring process and the index.
