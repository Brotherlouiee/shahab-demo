"""Best-effort Redis cache: PostgreSQL remains the source of truth."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime
from typing import Any, cast

from redis import Redis
from redis.exceptions import RedisError

from backend.app.questionnaire.domain.session import QuestionnaireSession


class RedisQuestionnaireSessionCache:
    def __init__(self, client: Redis) -> None:
        self._client = client

    def get(self, session_id: str) -> QuestionnaireSession | None:
        try:
            payload = cast(str | bytes | None, cast(Any, self._client).get(self._key(session_id)))
        except RedisError:
            return None
        if not payload:
            return None
        try:
            data = json.loads(payload)
            return QuestionnaireSession(
                uuid.UUID(data["sessionId"]),
                data["questionnaireVersion"],
                datetime.fromisoformat(data["createdAt"]),
                datetime.fromisoformat(data["expiresAt"]),
            )
        except (KeyError, TypeError, ValueError):
            return None

    def set(self, session: QuestionnaireSession) -> None:
        ttl = max(0, int((session.expires_at - datetime.now(session.expires_at.tzinfo)).total_seconds()))
        if ttl <= 0:
            self.delete(str(session.session_id))
            return
        payload = json.dumps(
            {
                "sessionId": str(session.session_id),
                "questionnaireVersion": session.questionnaire_version,
                "createdAt": session.created_at.isoformat(),
                "expiresAt": session.expires_at.isoformat(),
            },
            separators=(",", ":"),
        )
        try:
            self._client.set(self._key(str(session.session_id)), payload, ex=ttl)
        except RedisError:
            pass

    def delete(self, session_id: str) -> None:
        try:
            self._client.delete(self._key(session_id))
        except RedisError:
            pass

    def close(self) -> None:
        self._client.close()

    @staticmethod
    def _key(session_id: str) -> str:
        digest = hashlib.sha256(session_id.encode("utf-8")).hexdigest()
        return f"shahab:questionnaire:session:{digest}"
