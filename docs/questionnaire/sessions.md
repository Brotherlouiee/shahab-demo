# Anonymous questionnaire sessions — US-07.T03

Sessions carry only an opaque identifier, questionnaire version, expiry and canonical answers. They never carry identity, IP data, raw source, browser URL state or UI indexes.

A caller supplies the lifetime through QuestionnaireRetentionPolicy. No default production TTL, automatic deletion job, or cross-device resume behavior is introduced: those product/privacy decisions remain pending. At expiry, reads and writes are rejected.

This task deliberately adds no HTTP endpoint, query-string answer transport, browser persistence, identity, scoring, ranking or frontend wiring.
