# US-10.T03 — Operations audit threat review

Assets: provenance, reviewed plans, approval history and internal workflow head.
Trust: T01 fresh server grants and T02 coordinator. Mock OTP/customer roles are
never operator credentials; constructing an identity is not verification.

| Threat | Control and verification |
| --- | --- |
| Rewrite/delete history through ORM or raw SQL | PostgreSQL statement triggers reject UPDATE/DELETE/TRUNCATE; tests include approval view writes. No automatic retention purge. |
| Import retry overwrites actor/source/time | Unique import code, singleton lock, exact evidence/actor/reason match; return first event or reject conflict. |
| Stale/forged approval or rollback | Immutable FK-linked import/version, legal transition checks, original approval retained; current pointer CAS under lock. |
| Event insert fails after state change | Same transaction rolls back pointer/aggregate/event; real DB injected-failure tests for all five mutations. |
| Concurrent workers lose a transition | Database row lock, fresh state validation; two independent connections prove one successful same-target publication/rollback. |
| Payload deserialization executes code or reinterprets history | Strict versioned Pydantic JSON codec, no pickle/re-normalization, exact Decimal values, reject unknown schema/extra fields/nonfinite numbers. |
| Public API role escalation/exposure | No new route or production composition; deny-all remains. Protected credentials/tool are T04. |
| Secret/PII in evidence or logs | Use opaque internal actor reference and non-sensitive reason; no tokens/passwords/customer answers. Raw source evidence is internal-only, not public responses. |

Limit: database owner/superuser can change DDL/triggers. Before operational use,
T04 must grant a non-owner runtime role no ALTER/DROP/TRUNCATE permissions and
protect audit reads. External tamper-proof signing/export is not claimed.
A failed or denied command raises without success-event; no audit persistence
claim is made when PostgreSQL is unavailable. T04's transport should record a
redacted denial/security log separately, not fake a committed state transition.

## T04 اتصال ابزار

CLI از HTTPS introspection با issuer/audience/expiry/MFA و grant تازه استفاده
می‌کند. payload نمی‌تواند actor/role/source/config تعیین کند. redirect و TLS
نامعتبر رد؛ خطا و خروجی بدون credential هستند. DB role غیرمالک الزامی و حساب
مشتری خارج از grant است. public materializer و audit در یک transaction هستند.
محدودیت provider و scope رسمی در operations/protected-tool.md ثبت شده است.
