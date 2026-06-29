"""API key service — generation, hashing, and CRUD for user API keys."""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.models import ApiKey, User

KEY_PREFIX = "mafsk_"
KEY_DISPLAY_PREFIX_LENGTH = len(KEY_PREFIX) + 8
MAX_KEYS_PER_USER = 50
MAX_EXPIRATION_DAYS = 365
LAST_USED_THROTTLE = timedelta(hours=1)


class ApiKeyLimitReached(Exception):
    """Raised when a user has reached their API key limit."""


class InvalidExpiration(Exception):
    """Raised when the requested expiration date is invalid."""


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _hash_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


def generate_api_key() -> str:
    """Generate a new high-entropy API key with a recognizable prefix."""
    return f"{KEY_PREFIX}{secrets.token_urlsafe(32)}"


def create_api_key(
    db: Session, user: User, name: str, expires_at: datetime | None
) -> tuple[ApiKey, str]:
    """Create a new API key for the user.

    Returns the ORM object and the plaintext key, which is never stored
    and must be shown to the user immediately.
    """
    key_count = db.scalar(
        select(func.count()).select_from(ApiKey).where(ApiKey.user_id == user.id)
    )
    if key_count is not None and key_count >= MAX_KEYS_PER_USER:
        raise ApiKeyLimitReached(f"Maximum of {MAX_KEYS_PER_USER} API keys reached")

    now = _now()
    if expires_at is not None:
        if expires_at <= now:
            raise InvalidExpiration("expires_at must be in the future")
        if expires_at > now + timedelta(days=MAX_EXPIRATION_DAYS):
            raise InvalidExpiration(
                f"expires_at must be within {MAX_EXPIRATION_DAYS} days"
            )

    raw_key = generate_api_key()
    api_key = ApiKey(
        user=user,
        name=name,
        key_prefix=raw_key[:KEY_DISPLAY_PREFIX_LENGTH],
        key_hash=_hash_key(raw_key),
        expires_at=expires_at,
    )
    db.add(api_key)
    db.commit()
    return api_key, raw_key


def list_api_keys(db: Session, user: User) -> list[ApiKey]:
    """List a user's API keys, most recently created first."""
    return list(
        db.scalars(
            select(ApiKey)
            .where(ApiKey.user_id == user.id)
            .order_by(ApiKey.created_at.desc())
        )
    )


def delete_api_key(db: Session, user: User, key_id: int) -> bool:
    """Delete an API key owned by the user. Returns False if not found."""
    api_key = db.scalar(
        select(ApiKey).where(ApiKey.id == key_id, ApiKey.user_id == user.id)
    )
    if api_key is None:
        return False
    db.delete(api_key)
    db.commit()
    return True


def authenticate_api_key(db: Session, raw_key: str) -> User | None:
    """Return the User owning a valid, non-expired API key, or None."""
    if not raw_key.startswith(KEY_PREFIX):
        return None

    api_key = db.scalar(select(ApiKey).where(ApiKey.key_hash == _hash_key(raw_key)))
    if api_key is None:
        return None

    now = _now()
    if api_key.expires_at is not None and api_key.expires_at <= now:
        return None

    if api_key.last_used_at is None or now - api_key.last_used_at > LAST_USED_THROTTLE:
        api_key.last_used_at = now
        db.commit()

    return api_key.user
