# Questionnaire backend boundary

This bounded context owns the approved, versioned questionnaire configuration
and its framework-independent validation. It does not own HTTP routes, browser
navigation, sessions, persistence, recommendation scoring, or raw-source
mutation. Those responsibilities are introduced only in their respective
US-07 tasks.

The public configuration loader is `domain.configuration.load_questionnaire_configuration`.
It accepts the committed configuration artifact only after validating canonical
IDs and structural invariants; callers must not infer answers from UI indexes.
