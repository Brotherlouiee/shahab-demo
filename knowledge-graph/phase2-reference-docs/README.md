# Shahab Phase 2 Reference Graph

This package contains a source-pinned semantic graph for the two reference documents only. Start with `GRAPH_REPORT.md`, then inspect `semantic/graph.json` and `semantic/validation.json`. Chunks, evidence-review ledgers, quarantine provenance and resumable checkpoints are included.

```sh
graphify query "approved wallet ownership and credit source" --graph knowledge-graph/phase2-reference-docs/semantic/graph.json
graphify path docs_shahab_phase_2_development_blueprint_wallet_credit_types_and_rights docs_shahab_digital_wallet_wallet_ownership_model --graph knowledge-graph/phase2-reference-docs/semantic/graph.json
graphify explain docs_shahab_digital_wallet_wallet_ownership_model --graph knowledge-graph/phase2-reference-docs/semantic/graph.json
python knowledge-graph/phase2-reference-docs/tools/validate_graph.py --repo . --graph knowledge-graph/phase2-reference-docs/semantic/graph.json --structural knowledge-graph/phase2-reference-docs/structural/graph.json --progress knowledge-graph/phase2-reference-docs/checkpoints/progress.json --chunks knowledge-graph/phase2-reference-docs/chunks --reviews knowledge-graph/phase2-reference-docs/relation-review --corrections knowledge-graph/phase2-reference-docs/corrections-exact.json
```

The validator requires the reviewed correction ledger as well as the source, chunks, structural graph, and relation reviews. It rejects unreviewed graph records and quarantines that do not match the ledger. Inferred and ambiguous edges are navigation hints only; they do not create approved requirements. See the report for coverage and Graphify's internal clustering limitation.
