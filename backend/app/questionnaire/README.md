# Questionnaire backend boundary

This bounded context owns approved questionnaire configuration, anonymous session contracts and framework-independent canonical-answer validation. It does not own HTTP routes, browser navigation, identity, scoring or raw-source mutation.

The domain rejects an answer unless it belongs to the exact canonical question. Session lifetime is caller-supplied; no default production TTL, deletion job or URL answer transport is introduced in US-07.T03.
