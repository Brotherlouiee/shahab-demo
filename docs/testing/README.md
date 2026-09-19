# Testing documentation

برنامه و evidence تست‌های unit، integration، API، E2E، data-audit، security و release gate در این پوشه ثبت می‌شوند. هر تسک فقط با تست مرتبطِ سبز قابل عبور است.

## US-06.T04 evidence

`backend.tests.test_loan_detail_api` uses an approved-serving repository override
to verify the versioned detail response, parsed plain-text bullets, omitted
internal fields, typed absent-detail response and typed unavailable-catalogue
response. `npm run build` compiles the active RTL React integration. Browser/E2E
coverage for loading, error, empty, invalid logo/link and XSS rendering remains
the explicit scope of `US-06.T05`.
