# Graphify query checks

The following Graphify CLI calls were executed against `../semantic/graph.json` (Graphify 0.9.112):

```sh
graphify query 'Summarize wallet credit ownership rights and source distinctions' --graph semantic/graph.json --seed docs_shahab_digital_wallet_wallet_ownership_model --depth 1 --budget 1400
graphify path docs_shahab_phase_2_development_blueprint_wallet_credit_types_and_rights docs_shahab_digital_wallet_wallet_ownership_model --graph semantic/graph.json
graphify explain docs_shahab_digital_wallet_wallet_ownership_model --graph semantic/graph.json
```

All returned output. The Blueprint-to-Wallet path is one hop, `conceptually_related_to`, classified `INFERRED` at 0.75. Treat this as a discovery lead, not an approved cross-document requirement. The source text and line witnesses remain on the edge; consult both before deriving tasks. Query results are navigation, not policy authority.
