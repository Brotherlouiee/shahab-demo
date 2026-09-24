# Anonymous questionnaire sessions — US-07.T04

## Confirmed retention and resume contract

The product owner confirmed a **30-minute** anonymous-session lifetime on 2026-09-24.

- A session contains only an opaque identifier, questionnaire version, expiry and canonical question/answer pairs.
- The identifier is held only in the active React instance. It is not included in URLs, localStorage, sessionStorage, analytics or public logs.
- Back/forward navigation within the active questionnaire view reuses the in-memory session. Refreshing, closing the tab, opening another tab or changing devices starts a new session; cross-device resume is out of scope.
- At expiry, reads and writes return a typed safe error. The UI leaves the user on the current question and presents a retryable message.
- A canonical answer is sent only in the JSON body of the answer-write request. Screen indexes and option positions are never sent as answer identities.

## Scope boundary

This task introduces no identity, credit decision, score, recommendation result, automatic deletion job, production persistence guarantee or public deployment. The current server adapter is an explicit development composition boundary; production storage/operational hardening remains ordered future work.
