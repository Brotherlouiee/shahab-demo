# Security guidance

Use defense in depth. Create and maintain a threat model before backend/persistence work. Minimize questionnaire and identity data; document purpose, retention and deletion. Keep secrets only in a secret manager/environment, never in code, client builds, logs or commits.

Validate all API input at the server boundary, enforce authorization at use cases with ownership checks, use HTTPS, tight CORS, rate limiting, safe errors and CSRF protection for cookie sessions. Use least-privilege database roles, parameterized queries, encryption at rest for sensitive data, encrypted backups and append-only audit events for loans, weights and configuration.

Treat client-side scores as display-only. Canonical scoring/config decisions must be server-controlled for any tamper-resistant production claim. Render external conditions as text, prevent XSS, validate imported files, lock dependencies and scan source/build/CI for vulnerabilities and secrets.

Run SAST, dependency/secret scanning, staging DAST and scenario tests for validation, authentication, authorization/IDOR, CSRF, XSS, injection, rate limits, headers/CORS, score tampering, logging/retention and restore. Critical/high exploitable findings, leaked secrets, auth bypass, confirmed XSS, sensitive-data exposure or untested backups block release.
