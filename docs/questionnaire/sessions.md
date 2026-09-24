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


## US-07.T05 verification boundary

- Browser coverage verifies the RTL radiogroup and named controls, blocks an unanswered behavioural screen, and confirms that same-tab back navigation preserves the selected canonical option.
- The browser test intercepts the session contract and asserts a single POST session request followed by a PUT answer request with the canonical JSON `answerId`; the answer and opaque ID do not appear in the browser URL.
- On a session-start failure, the page remains on the question and exposes a retryable `role="alert"`; it does not advance with an unconfirmed answer.
- API tests cover canonical answer ownership, safe unknown-session errors and rejection of an answer supplied outside the JSON body.

These are completion tests for the current in-memory development adapter. They do not claim restart survival, durable storage, Redis availability or cross-tab/cross-device resume; those are acceptance criteria for **US-07.T06**.
