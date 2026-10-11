# Internal operations authorization — US-10.T01

`policy.py` owns the pure role/permission matrix. `authorization.py` owns the
current-grant port and checks trusted identity, expiry and explicit authority.
It does not import FastAPI, ORM, customer accounts or recommendation code.

Use `OperationsAuthorizer.require(identity, permission)` before operational
storage access in T02. The identity is issued by the independently authenticated
internal adapter in T04; never deserialize it from the client's JSON. Ordinary
customer OTP (including the development code) cannot issue this identity.

The app defaults to a deny-all grant repository. No operator is seeded and no
phone allowlist, shared bearer credential, role endpoint or grant migration is
introduced. T02/T03/T04 retain their independent integration/audit/authentication
acceptance. See `docs/operations/authorization.md` for the threat boundaries.
