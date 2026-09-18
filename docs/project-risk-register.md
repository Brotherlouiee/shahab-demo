# Initial project risk and ambiguity register — US-01.T05

## Scope and handling

This register records baseline risks and open ambiguities without changing product behavior, source interpretation, security posture, or recommendation logic. A risk is not silently accepted: its owner, affected story, next action, and gate are explicit. Product/data decisions belong in an ADR or `docs/recommendation-data-decisions.md`, not in this register.

| ID | Category | Risk or ambiguity | Likelihood | Impact | Affected story | Status | Owner | Required next action / gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R-001 | Source data | The six UTF-16 LE sources may be accidentally transcoded in a future edit. | Medium | High | US-02, US-05 | Controlled | Data owner | Preserve byte-safe workflow and rerun hash/byte identity verification before consumption. |
| R-002 | Data semantics | Data sources can contain conflicting weights, categories, formats, or ranges. | High | High | US-02 | Open | Product owner + data owner | Run data-audit; record every conflict with provenance and an approved/versioned decision. |
| R-003 | Ranking integrity | Unknown core values could produce misleading ranked recommendations if treated as neutral. | Medium | High | US-02, US-08 | Controlled by guide | Product owner | Enforce exclusion for four core variables; golden tests must prove the policy. |
| R-004 | Privacy | The prototype stores personal name and phone information in browser `localStorage`. | High | High | US-07, US-11 | Open | Security owner | Define retention and session storage policy; remove/redesign client persistence before real authentication. |
| R-005 | Authentication | OTP is client-only and accepts a fixed code; Kavenegar activation is deferred pending legal/onboarding steps. | High | High | US-07, US-11 | Open | Product owner + security owner | Keep only a server-side mock provider behind a port; do not present it as real verification; integrate Kavenegar only after credentials/legal approval. |
| R-006 | Architecture | The active UI module and stylesheet are large and routing is custom History API code. | High | Medium | US-03, US-07, US-09 | Open | Technical owner | Add characterization tests and feature boundaries before incremental extraction; preserve public routes. |
| R-007 | Quality | No lint, typecheck, automated tests, or CI exists in the baseline. | High | High | US-03 | Open | Technical owner | Establish locked quality gates and CI before backend/domain implementation. |
| R-008 | Dependency supply chain | `package.json` uses broad/latest version ranges. | Medium | Medium | US-03, US-11 | Open | Technical owner | Pin/lock, scan dependencies, and define update policy before production deployment. |
| R-009 | Hosting/security | Two UI images depend on remote Unsplash URLs without an explicit allowlist/fallback decision. | Medium | Low | US-09, US-11 | Open | Technical owner | Add asset fallback and security/content policy in UI hardening. |
| R-010 | Runtime environment | Docker/Compose is unavailable in the current execution environment. | Medium | High | US-03, US-04, US-05 | Open | Environment owner | Install/verify Docker Compose in the target local environment before Docker-dependent tasks; do not bypass PostgreSQL gates with SQLite only. |
| R-011 | Database integrity | There is no PostgreSQL schema, migration, approval workflow, or append-only audit trail yet. | High | High | US-04, US-05, US-10 | Open | Data/technical owner | Implement normalized schema, PostgreSQL migration tests, controlled publish flow, and audit records in their assigned stories. |
| R-012 | Product communication | A user may mistake a match score for credit approval likelihood or a guaranteed loan result. | Medium | High | US-08, US-09 | Open | Product owner | Test disclosure copy: the score compares conditions with preferences only and never guarantees approval. |
| R-013 | Source freshness | Bank terms may change after the supplied data snapshot. | High | High | US-05, US-06, US-10 | Open | Data owner | Model `sourceUrl`, `sourceCheckedAt`, data version, approval and rollback before serving loans. |

## Exit gate for US-01

- Baseline build is reproducible.
- Repository, mock, route, dependency, source, and risk inventories are documented.
- All six canonical source files are byte-verified.
- Documentation skeletons, ADR template, CHANGELOG, and canonical current-state checkpoint exist.
- No product logic changed in US-01.

`US-02` may begin only after the PR review/merge gate is complete and no US-01 blocker remains open.
