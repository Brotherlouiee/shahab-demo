# US-09.T05A — source and database review

The six `.agents/documents/*.unitext` files are immutable UTF-16LE sources. D-005 selects **only** `تبدیل پاسخ‌ها به وزن‌های عددی.unitext` for question/answer weights. Numeric values in the questionnaire-to-variable mapping matrix are ignored. The distinct one-to-one coefficient source supplies answer/category compatibility. No raw source byte is modified.

## Reproducible source evidence

From the repository root, run:

```sh
python -m scripts.audit_source_weight_conflicts
python -m scripts.audit_t05a_sources
python -m scripts.build_t05a_import_manifest --output /tmp/t05a-loans.json
python -m scripts.build_t05a_recommendation_config > /tmp/t05a-config.json
```

The verified extraction has 102 loans and 102 nonempty conditions, 88 ranking eligible and 14 needs review due to unclassified core values. It supplies 30 question/variable groups, 150 answer weights and 720 answer/category compatibility cells; each of eight variables has a category/state assignment for all 102 rows. Five numeric differences in the mapping matrix are informational because the conversion table has precedence. Three above-cap `maxAmount` values (40/50 billion toman) remain unclassified rather than extrapolated. See `docs/data-audit/t05a-source-audit.json` and `docs/data-audit/t05a-weight-audit.json` for rows and causes.

## Database scope and publication

The repository supplies a Docker Compose PostgreSQL service with a local named
volume, and GitHub Actions starts a disposable PostgreSQL service for tests.
`netlify.toml` builds only the frontend. No continuously hosted PostgreSQL
instance or production database connection is established by this repository.
The source audit and CI prove the import against the disposable test database;
they do not imply that the 102 loans were already placed in a deployed database.

For a local Compose run, keep the named volume and use the project-local `.env`
according to the existing Docker runbook. For a future persistent deployment,
provision PostgreSQL separately and supply its connection securely. In either
case, inspect the chosen database before publication.

Apply the reviewed Alembic migration in the chosen environment using the existing operations process, then set `SHAHAB_DATABASE_URL` from that environment. First run the read-only inventory:

```sh
python -m scripts.materialize_t05a
```

Compare its existing published versions, source hash, assignments, conditions, config and active version with the source audit. The read-only report lists missing/unexpected source rows, identity and conditions mismatches, incomplete rows and individual category/state discrepancies for all eight variables. Review those differences before any write. If any published loan version already exists without this exact active official catalogue, publication fails closed before writing; reconcile/reuse the existing rows in a separately reviewed backfill. If any existing source row or config conflicts, publication fails closed; do not delete records to make a count match.

After source and database review, an authorized operator can execute:

```sh
python -m scripts.materialize_t05a --publish --actor-reference OPERATOR_REFERENCE --approval-reason 'Reviewed official source and database difference'
```

Publication requires explicit actor/reason, validates exact reviewed manifest digests, and commits all rows and the active pointer in one transaction. The identical active version is reused. The previous pointer is marked superseded only in the same transaction. On failure the transaction rolls back; repair the reviewed input or migration and rerun the read-only inventory. Downgrading the migration removes these new tables and must be planned against retained catalogue history; do not use it as an operational rollback of published data. No persistent deployment or publication outside the disposable CI database is claimed by the tests. T05B supplies read adapters; T06 supplies the live endpoint and browser journey.
