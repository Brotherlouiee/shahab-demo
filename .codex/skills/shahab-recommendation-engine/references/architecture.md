# Architecture guidance

Keep Shahab modular by feature, then by layer: `domain` is framework-free; `application` coordinates use cases; `infrastructure` implements external adapters; `presentation` maps UI input/output. Dependencies point inward and only the composition root wires concrete implementations.

Use small ports such as `LoanRepository`, `RecommendationConfigRepository`, and `RecommendationEngine`. UI must never parse Excel, select source data, or calculate scores. Keep parsers, scoring, tree traversal, normalization, trace construction and details rendering in separate focused modules.

Use versioned schema/config/data decisions. An adapter may change from JSON to API without changing the engine or components. Unknown core ranking data goes to `needsReview`, not a neutral score; unknown deposit-related data is neutral and traced.

When adding a feature, place it by responsibility: rules in engine/config, new sources in adapters, question text in questionnaire config, filters in presentation, and administration/authentication in separate features. Do not place domain-specific logic in `shared` or create vague `utils` folders.

Before cross-layer refactoring, write characterization tests. Keep refactors separate from behavioral changes, prevent circular imports, keep public exports narrow, and record important tradeoffs as an ADR. Done requires architecture-boundary checks, relevant tests, versioned decisions, traceability and a safe rollback/config path.
