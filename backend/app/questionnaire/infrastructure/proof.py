"""Server-verified per-questionnaire capability, independent of ID and Redis cache.

Only a SHA-256 digest persists in PostgreSQL. The random secret exists in the
creator's HttpOnly cookie, never JSON, URL, answer cache or application logs.
Bound sessions additionally require the exact active account generation. Locks
serialize reads/writes with first owner claim; callers recheck after a commit.
"""

import hashlib
import hmac
import re
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.accounts.identity import AccountActor, require_active_account
from backend.app.api.errors import ApiError, ErrorCode
from backend.app.infrastructure.db.models import QuestionnaireSession, QuestionnaireSessionState
from backend.app.questionnaire.infrastructure.memory_sessions import InMemoryQuestionnaireSessionRepository

PROOF_COOKIE_PREFIX = "shahab_questionnaire_proof_"


def proof_digest(secret: str) -> str:
    return hashlib.sha256(secret.encode("ascii")).hexdigest()


def require_questionnaire_access(
    session_id: str,
    secret: str | None,
    actor: AccountActor | None,
    db: Session | None,
    local_repository: InMemoryQuestionnaireSessionRepository,
) -> None:
    """Deny missing/forged/legacy/other-owner proof before reading any answers.

    Nonexistence and invalid proof share 403. A matching expired proof retains
    the existing 410 contract; neither refresh nor owner binding renews expiry.
    SQL authority is freshly locked; cached metadata is not trusted for access.
    """
    denied = ApiError(status_code=403, code=ErrorCode.FORBIDDEN, message="Questionnaire access is not allowed.")
    if secret is None or re.fullmatch(r"[A-Za-z0-9_-]{43}", secret) is None:
        raise denied
    try:
        identifier = uuid.UUID(session_id)
    except ValueError:
        raise denied from None
    owner = None
    expired_state = False
    if db is None:
        row = local_repository.get(str(identifier))
        digest = row.creator_proof_digest if row is not None else None
        expires = row.expires_at if row is not None else None
    else:
        if actor is not None:
            require_active_account(actor.account_id, db)
        stored = db.scalar(
            select(QuestionnaireSession)
            .where(QuestionnaireSession.questionnaire_session_id == identifier)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        digest = stored.creator_proof_digest if stored is not None else None
        expires = stored.expires_at if stored is not None else None
        owner = stored.owner_account_id if stored is not None else None
        expired_state = stored is not None and stored.state == QuestionnaireSessionState.EXPIRED
    if digest is None or not hmac.compare_digest(digest, proof_digest(secret)):
        raise denied
    if owner is not None and (actor is None or actor.account_id != owner):
        raise denied
    if expires is None:
        raise denied
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=UTC)
    if expired_state or datetime.now(UTC) >= expires:
        raise ApiError(status_code=410, code=ErrorCode.NOT_FOUND, message="Questionnaire session has expired.")
