-- Run as the schema owner AFTER reviewed migrations, on the selected database.
-- Create shahab_api separately with LOGIN and a private password; it must not be
-- an owner, superuser, DDL-capable role or member of the migration/operator role.
-- No default privileges: new schema objects require an explicit grant review.
SELECT format('GRANT CONNECT ON DATABASE %I TO shahab_api', current_database()) \gexec
GRANT USAGE ON SCHEMA public TO shahab_api;
GRANT SELECT ON
    lenders, loan_products, loan_product_versions, loan_terms, loan_variables,
    variable_categories, loan_category_assignments, loan_conditions,
    loan_serving_facts, questionnaire_versions, questions, answer_options,
    recommendation_config_versions, question_variable_weights,
    answer_option_weights, answer_category_compatibilities,
    serving_catalogue_versions, serving_catalogue_members,
    data_import_runs, data_source_files, alembic_version,
    accounts, account_access_sessions, account_otp_challenges,
    account_otp_quota_events, user_profiles, questionnaire_sessions,
    questionnaire_answers, recommendation_history_runs,
    recommendation_history_items, recommendation_history_item_reasons,
    account_bookmarks TO shahab_api;
-- Existing API startup idempotently initializes the canonical reference IDs.
GRANT INSERT ON questionnaire_versions, questions, answer_options TO shahab_api;
GRANT INSERT, UPDATE ON accounts, user_profiles, account_access_sessions,
    account_otp_challenges, questionnaire_sessions, questionnaire_answers,
    account_bookmarks TO shahab_api;
GRANT INSERT, DELETE ON account_otp_quota_events TO shahab_api;
GRANT DELETE ON account_access_sessions, account_otp_challenges,
    questionnaire_sessions, questionnaire_answers TO shahab_api;
GRANT INSERT ON recommendation_history_runs, recommendation_history_items,
    recommendation_history_item_reasons TO shahab_api;
GRANT UPDATE (hidden_at) ON recommendation_history_runs TO shahab_api;
-- Deliberately no operations/audit access, catalogue writes, sequence/DDL rights,
-- TRUNCATE, DELETE of accounts/history, or schema ownership.
