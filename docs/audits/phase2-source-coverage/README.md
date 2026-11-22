# Phase 2 Source Coverage — structural baseline

This directory contains a reproducible **snapshot** extracted from the approved Blueprint and Wallet blobs on the PR #251 branch.

- Source inventory: **384** units (326 headings, 58 Markdown tables).
- Paragraph candidates: **1110**. These are **not** verified atomic requirements; each must be semantically classified, split if compound, and checked against source decisions.
- Execution trace: deliberately **UNVERIFIED**; do not interpret blank package/requirement/task/test cells as proof of absence or coverage.
- Counts are based on Markdown headings and tables containing separator rows, not raw pipe-delimited text blocks.
- No package content or gate status has been changed.

## Required next step

Perform source-by-source semantic review, expand multi-obligation tables and paragraphs into atomic obligations, reconcile with Graphify and all 36 packages, then populate verified execution trace with evidence. Only after that may C12a or coverage gates be evaluated.

Source blob SHAs and extraction counts are recorded in `extraction-manifest.json`.
