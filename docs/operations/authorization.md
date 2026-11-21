# Operations authorization — US-10.T01

## Scope and current availability

This task supplies a server-side authorization boundary and an explicit policy.
It does **not** supply a management panel, operator credential verifier, persistent
role assignments, public role-management endpoint or fully guarded pipeline.
The app's `operations_authorizer` uses a deny-all repository. No account is
automatically an administrator, including the product owner or a phone that
successfully enters the local mock OTP.

US-09.T07 and the online portion of US-09.T081 remain open until approved hosting.
The owner authorized the independent T01 foundation on 2026-10-11; this is not
an exception to production authentication, audit or final release gates.

## Explicit least-privilege policy

| Role | Import | Review issues | Approve data | Publish data | Roll back data | Edit config | Approve config |
| --- | --- | --- | --- | --- | --- | --- | --- |
| anonymous | No | No | No | No | No | No | No |
| user | No | No | No | No | No | No | No |
| support | No | No | No | No | No | No | No |
| data-editor | Yes | Yes | No | No | No | Yes | No |
| admin | No | No | Yes | Yes | Yes | No | Yes |
| service | Yes | No | No | No | No | No | No |

There is no wildcard or role inheritance. Explicit editor + admin grants combine
their permissions; an admin alone cannot import/edit. Service credentials can
use only service grants, and human credentials cannot borrow service grants.
No permission is created by profile fields, a role header, customer phone or
frontend state. These grants do not confer access to customer profile/history.

## Identity and enforcement contract

1. T04's reviewed internal credential adapter must issue `OperationsIdentity`
   with a canonical opaque subject and short expiry after verifying human MFA or
   an independent service credential. Do not deserialize this object from JSON.
   The current customer/mock OTP adapter does not qualify.
2. A trusted `RoleGrantRepository` resolves that exact subject's current role
   binding, with aware expiry. Each operation rereads it: no long-lived role
   cache or grant embedded in a customer token. A missing grant represents
   revocation. Deny-all is the default if no adapter is configured.
3. T02 must call `require(identity, permission)` before each operations use case
   touches persistence. It returns the verified actor reference for later audit.
   Neither a route-only check nor a non-empty `actor_reference` is sufficient.
4. Permission denial raises `OperationsAccessDenied`; authority lookup failure
   raises `OperationsAuthorityUnavailable`. Both messages omit actor/credential/
   repository details. The T04 CLI returns a safe failure/exit status without bypass; no HTTP operations endpoint is installed.
5. Wrong-subject grants, naive/expired timestamps, empty/unknown roles, raw
   permission strings and unsupported identity kinds fail closed.

## Boundaries retained for following tasks

Existing trusted internal pipeline services and CLI commands still have their
existing OS/operator trust boundary; **T01 alone does not retrofit them with
RBAC**. Do not expose them as HTTP routes. T02 owns use-case enforcement and
resource/transition checks, T03 owns append-only audit, and T04 owns the guarded
transport/tool plus independently verified operator credentials. Persistent
grants, if required by that design, need their own reviewed schema/3NF/migration
plan; no speculative tables or SQL edits are introduced here.

## Threat review

| Threat | Control delivered | Remaining gate |
| --- | --- | --- |
| Customer/mock OTP escalates to admin | Separate identity kind; reject before grant lookup; public profile fields remain allowlisted | T04 authenticates internal credential |
| Caller spoofs role/permission/subject | Roles come only from trusted repository; exact subject match; explicit enum allowlist | T02 guards every use case, T04 verifies subject |
| Revoked/expired grant still works | Fresh lookup on each check; strict aware expiry | Trusted grant adapter and rotation/revocation integration |
| Service approves/configures data | Service identity is restricted to service role and import | T03 audit and publication approval |
| Misconfigured/unavailable authority grants access | Deny-all default; typed unavailable failure without fallback | T04 operational monitoring |

## Validation and rollback

`python -m unittest backend.tests.test_operations_authorization` covers all
42 role/permission pairs and failure paths. HTTP checks use FastAPI TestClient
with a declared DB double for public contract checks, not persistence proof.
Existing OTP/profile regressions remain intact; CI retains its real PostgreSQL
and browser suites.

Rollback reverts the policy and app composition change. There is no schema,
grant seed, data/config version, API contract or customer UI change to reverse.

## US-10.T02 enforcement delivered

The internal coordinator now checks each exact permission before any review/version repository access. Preparation and publication require nonempty reasons and aware UTC decisions as do import/approval/rollback; port decisions retain the actual verified actor independently of original approval. Stored resource linkage blocks mismatched or partially accepted imports. Stale or failed rollback leaves the pointer and decision unchanged in the explicit local/test contract model. No public route, durable adapter or real verifier is enabled; T03/T04 and hosting gates remain open. See [data-use-cases.md](data-use-cases.md).

## وضعیت پس از T04/T05

مطالب بالا محدوده تاریخی T01 را شرح می‌دهند. اکنون T02 کنترل use case، T03
adapter/audit دائمی و T04 verifier HTTPS و CLI خصوصی را تحویل داده‌اند. app عمومی
همچنان deny-all است؛ provider واقعی اپراتور هنوز فعال نشده. دستورهای اجرایی و
آموزش در [راهنمای T05](operations-runbook.md) و قرارداد [T04](protected-tool.md)
هستند. permissionهای config سیاست‌اند؛ command تغییر config یا وزن در ابزار
فعلی وجود ندارد و SQL دستی جای آن نیست.
