# Architecture Decision Records

This directory records the significant architecture decisions made on this
project, using the lightweight [ADR](https://adr.github.io/) format
(Michael Nygard's template).

Each record is immutable once accepted. When a decision changes, we do **not**
edit the old record — we add a new ADR that supersedes it and update the status
of the old one to point at its replacement.

## Process

1. Copy the template structure of an existing record.
2. Number it sequentially (`NNNN-kebab-case-title.md`).
3. Open it with status `Proposed`, discuss, then set to `Accepted`.
4. Add a line to the index below.

## Index

| #    | Title                                                                            | Status   |
| ---- | -------------------------------------------------------------------------------- | -------- |
| 0001 | [Record architecture decisions](0001-record-architecture-decisions.md)           | Accepted |
| 0002 | [API key storage and authentication](0002-api-key-storage-and-authentication.md) | Accepted |
