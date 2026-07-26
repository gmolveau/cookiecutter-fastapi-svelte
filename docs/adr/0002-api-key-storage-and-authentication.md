# 2. API key storage and authentication

Date: 2026-06-16

## Status

Accepted

## Context

In addition to interactive login (OAuth2 / Keycloak, stored in a signed session
cookie), users need a way to authenticate programmatic clients — scripts, CI,
integrations. The mechanism is a user-generated **API key** presented as a
bearer token.

This raises several questions that need a deliberate decision:

- What does a key look like, and how is it generated?
- How is it stored at rest? Leaking the keys table must not leak usable
  credentials.
- How is an incoming key verified on each request, and how fast is that?
- How do API keys coexist with the existing session-cookie auth?

The relevant code lives in:

- `backend/src/services/api_keys.py` — generation, hashing, CRUD, verification
- `backend/src/models.py` — the `ApiKey` ORM model
- `backend/src/services/authentication.py` — credential precedence
- `backend/src/dependencies.py` — FastAPI dependencies that extract credentials
- `backend/src/routes/api_keys.py` / `schemas/api_keys.py` — HTTP surface

## Decision

### Key format

A key is `mafsk_` + `secrets.token_urlsafe(32)`. The `secrets` module gives a
cryptographically secure random value (~256 bits of entropy); the `mafsk_`
prefix makes keys recognisable in logs/secret scanners and lets us cheaply
reject obviously-foreign tokens before touching the database.

### Storage at rest — hash only, never the plaintext

We store **only a SHA-256 hash** of the key (`ApiKey.key_hash`,
`String(64)`, `unique`, `index`). The plaintext key is returned to the user
exactly once, in the `POST /api-keys` response (`ApiKeyCreateResponse.key`), and
is never persisted. If it is lost, the user creates a new key.

Alongside the hash we store a non-secret **display prefix** (`key_prefix`, the
first 14 characters: `mafsk_` + 8 chars of the random body). This lets the UI
show "which key is this" in a list without ever revealing the secret.

A leak of the `api_keys` table therefore exposes no usable credential — only
hashes and display prefixes.

### Why SHA-256 and not bcrypt / argon2

Password hashing (bcrypt, argon2, scrypt) is deliberately slow and salted to
resist brute force against *low-entropy* human passwords. API keys here are
*high-entropy* random values (256 bits): brute forcing the preimage is
infeasible regardless of hash speed, so a slow KDF buys no meaningful security.

A fast, deterministic, unsalted hash is in fact required by our access pattern:
verification is a single indexed equality lookup
(`WHERE key_hash = sha256(presented)`), which is O(1) on the unique index. A
salted KDF would force a full table scan (one hash comparison per stored row)
on every authenticated request, which does not scale.

### Verification flow

`authenticate_api_key()`:

1. Reject the token early if it lacks the `mafsk_` prefix.
2. Look the key up by `key_hash`.
3. Reject if expired (`expires_at <= now`).
4. Update `last_used_at`, **throttled to once per hour**
   (`LAST_USED_THROTTLE`), so we don't write to the DB on every single request.
5. Return the owning `User`.

### Coexistence with session auth — bearer is authoritative

Credential resolution is centralised in `resolve_user()` and is intentionally
decoupled from FastAPI's `Request`. The precedence rule is:

- If an `Authorization: Bearer <token>` header is present, it is the **only**
  credential consulted. An *invalid* bearer token raises `NotAuthenticated` and
  does **not** silently fall back to the session cookie.
- With no bearer token, the session subject (`sub`) is used.

This avoids a confused-deputy class of bug where a broken/expired API key would
unexpectedly act as the cookie-authenticated browser user.

### Limits and lifecycle

Enforced in `create_api_key()`:

- Max **50** keys per user (`MAX_KEYS_PER_USER`).
- Expiry is optional; when set it must be in the future and within **365 days**
  (`MAX_EXPIRATION_DAYS`).
- Keys are owned by a user and deleted (revoked) by id; the ORM relationship
  cascades on user deletion (`ondelete="CASCADE"` +
  `cascade="all, delete-orphan"`).

## Consequences

- Compromise of the database does not yield usable API keys.
- A lost key cannot be recovered, only regenerated — acceptable and expected.
- Verification stays a single indexed lookup, cheap enough to run on every
  request.
- Time-bound `last_used_at` is accurate only to within ~1 hour by design.
- Migrating away from SHA-256 (e.g. to a peppered HMAC) would require either a
  re-hash-on-next-use scheme or invalidating existing keys, since we cannot
  recover plaintexts. If a pepper/HMAC is later desired for defence-in-depth,
  capture it in a superseding ADR.
- SHA-256 is the right call *only because* keys are high-entropy and
  randomly generated. This reasoning must not be copied to any low-entropy
  secret (e.g. passwords), which must use a slow KDF.
