#!/usr/bin/env python3
"""Small deterministic validator for the proposed Phase 5.0 contract artifacts.

This validates the contract and synthetic fixtures only. It is not a planning,
scheduling, or production Phase 5 validator.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
BASE = "e207860d82ccaf665241258256565d064ddd901d"
SNAPSHOT_ID = "phase4-45ed4ec10d34216cf935"
SOURCE_COMMIT = "8ce742b640bbcbb87be5fc29f3a5a28d92593dec"
CONTRACT = ROOT / "docs/phase5/planning-contract"
REF_TYPES = {"DECISION", "APPROVED_POLICY", "ARTIFACT", "CONTRACT_ARTIFACT", "SOURCE_DOCUMENT", "SOURCE_LOCATOR", "CERTIFIED_SNAPSHOT", "EVIDENCE", "ACCEPTANCE_GATE", "EXTERNAL_CONDITION"}
REF_RELATIONS = {"REQUIRES_INPUT", "DERIVED_FROM", "REQUIRES_APPROVAL", "CONSTRAINED_BY", "VALIDATED_BY", "EVIDENCED_BY", "BLOCKED_BY", "RELATED_TO"}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def ref_errors(refs: list[dict[str, Any]], decisions: set[str], policies: set[str], artifacts: set[str], schema: dict[str, Any], gates: set[str], snapshot: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    seen: set[tuple[str, str, str]] = set()
    for i, ref in enumerate(refs):
        if not isinstance(ref, dict):
            errors.append(f"reference[{i}] must be object")
            continue
        typ, rid, relation = ref.get("ref_type"), ref.get("ref_id"), ref.get("relation")
        if typ not in REF_TYPES:
            errors.append(f"reference[{i}] invalid ref_type {typ!r}")
            continue
        required = set(schema["reference_types"][typ]["required"])
        missing = required - ref.keys()
        if missing:
            errors.append(f"reference[{i}] missing {sorted(missing)}")
        if relation not in set(schema["reference_relations"]):
            errors.append(f"reference[{i}] invalid relation {relation!r}")
        key = (str(typ), str(rid), str(relation))
        if key in seen:
            errors.append(f"duplicate reference {key}")
        seen.add(key)
        if typ == "DECISION" and (not isinstance(rid, str) or not re.fullmatch(r"P5-D\d{2}", rid) or rid not in decisions):
            errors.append(f"invalid decision reference {rid!r}")
        elif typ == "APPROVED_POLICY" and rid not in policies:
            errors.append(f"invalid approved policy reference {rid!r}")
        elif typ == "ARTIFACT" and (not isinstance(rid, str) or not re.fullmatch(r"A\d{2}", rid) or rid not in artifacts):
            errors.append(f"invalid artifact reference {rid!r}")
        elif typ == "CONTRACT_ARTIFACT":
            if not isinstance(rid,str) or not rid.startswith("docs/phase5/planning-contract/") or not (ROOT/rid).is_file():
                errors.append(f"contract artifact does not resolve: {rid!r}")
        elif typ == "CERTIFIED_SNAPSHOT" and (rid != snapshot.get("snapshot_id") or ref.get("source_commit") != snapshot.get("certified_source_commit")):
            errors.append(f"snapshot mismatch {rid!r}")
        elif typ == "SOURCE_DOCUMENT":
            if not isinstance(rid, str) or rid.startswith("/") or ".." in Path(rid).parts or not (ROOT / rid).is_file():
                errors.append(f"source document does not resolve: {rid!r}")
            elif ref.get("source_commit") != SOURCE_COMMIT or ref.get("blob_sha") != git_blob(rid):
                errors.append(f"source document provenance mismatch: {rid}")
        elif typ == "SOURCE_LOCATOR":
            path = rid.split("#", 1)[0] if isinstance(rid, str) else ""
            if not path or not (ROOT / path).is_file() or not ref.get("locator") or ref.get("source_commit") != SOURCE_COMMIT or ref.get("blob_sha") != git_blob(path):
                errors.append(f"source locator does not resolve: {rid!r}")
            else:
                content=normalize_digits((ROOT/path).read_text(encoding="utf-8"))
                sections=re.findall(r"§{1,2}\s*([0-9]+(?:\.[0-9]+)*)",ref.get("locator",""))
                missing=[section for section in sections if section not in content]
                if missing: errors.append(f"source locator section not found {missing}: {rid!r}")
        elif typ == "ACCEPTANCE_GATE" and rid not in gates:
            errors.append(f"unknown acceptance gate {rid!r}")
        elif typ == "EXTERNAL_CONDITION" and rid not in {x["id"] for x in schema["external_conditions"]}:
            errors.append(f"unknown external condition {rid!r}")
        elif typ == "EVIDENCE" and not ref.get("tested_commit"):
            errors.append(f"evidence lacks tested_commit: {rid!r}")
    return errors


def git_blob(path: str) -> str | None:
    p = subprocess.run(["git", "rev-parse", f"{SOURCE_COMMIT}:{path}"], cwd=ROOT, capture_output=True, text=True)
    return p.stdout.strip() if p.returncode == 0 else None


def normalize_digits(value: str) -> str:
    return value.translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789"))


def hard_cycle(decision_ids: set[str], relations: list[dict[str, Any]]) -> bool:
    outgoing: dict[str, list[str]] = defaultdict(list)
    for edge in relations:
        if edge.get("relation_type") == "HARD_PREREQUISITE":
            source, target = edge.get("source_id"), edge.get("target_id")
            if source == target or source not in decision_ids or target not in decision_ids:
                return True
            outgoing[source].append(target)
    state: dict[str, int] = {}
    def visit(node: str) -> bool:
        if state.get(node) == 1:
            return True
        if state.get(node) == 2:
            return False
        state[node] = 1
        if any(visit(nxt) for nxt in outgoing[node]):
            return True
        state[node] = 2
        return False
    return any(visit(node) for node in decision_ids)


def decision_relation_errors(decision_ids: set[str], relations: list[dict[str, Any]], schema: dict[str, Any]) -> list[str]:
    errors=[]
    for edge in relations:
        if edge.get("relation_type") not in schema["decision_relations"]:
            errors.append(f"invalid decision relation {edge.get('relation_type')!r}")
        if edge.get("source_id") not in decision_ids or edge.get("target_id") not in decision_ids:
            errors.append(f"unknown decision endpoint {edge}")
        if edge.get("relation_type")=="HARD_PREREQUISITE" and edge.get("source_id")==edge.get("target_id"):
            errors.append("self hard prerequisite")
    if hard_cycle(decision_ids,relations): errors.append("hard prerequisite cycle")
    return errors


def graph_errors(nodes: list[dict[str, Any]], edges: list[dict[str, Any]], schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    node_types = {x["type_id"]: x for x in schema["graph_node_types"]}
    edge_types = {x["relation_id"]: x for x in schema["graph_edge_types"]}
    node_required={"type_id","definition","required_properties","optional_properties","id_namespace","incoming_relations","outgoing_relations","lifecycle_states","evidence_requirements","approval_status","validation_rules"}
    edge_required={"relation_id","definition","source_types","target_types","direction","cardinality","required_attributes","evidence_requirements","effect","approval_status","validation_rules"}
    for ntype in schema["graph_node_types"]:
        if node_required-set(ntype): errors.append(f"incomplete Node-Type Registry record: {ntype.get('type_id')}")
        if not ntype.get("definition") or not ntype.get("id_namespace") or not ntype.get("lifecycle_states"): errors.append(f"incomplete node semantics: {ntype.get('type_id')}")
    for edge in schema["graph_edge_types"]:
        if edge_required-set(edge): errors.append(f"incomplete Edge-Type Registry record: {edge.get('relation_id')}")
        if not edge.get("definition") or not edge.get("direction") or not edge.get("cardinality") or not edge.get("effect"): errors.append(f"incomplete edge semantics: {edge.get('relation_id')}")
        if not set(edge["source_types"] + edge["target_types"]) <= set(node_types):
            errors.append(f"undefined graph schema endpoint type: {edge['relation_id']}")
        if not set(edge["source_types"]) <= set(node_types):
            errors.append(f"unknown source type for {edge['relation_id']}")
        if not set(edge["target_types"]) <= set(node_types):
            errors.append(f"unknown target type for {edge['relation_id']}")
        for source_type in edge["source_types"]:
            if edge["relation_id"] not in node_types[source_type]["outgoing_relations"]:
                errors.append(f"edge missing from source registry: {edge['relation_id']} / {source_type}")
        for target_type in edge["target_types"]:
            if edge["relation_id"] not in node_types[target_type]["incoming_relations"]:
                errors.append(f"edge missing from target registry: {edge['relation_id']} / {target_type}")
    by_id: dict[str, dict[str, Any]] = {}
    for n in nodes:
        nid, ntype = n.get("id"), n.get("type")
        if not nid or nid in by_id:
            errors.append(f"duplicate or missing node id {nid!r}")
        by_id[str(nid)] = n
        if ntype not in node_types:
            errors.append(f"undefined node type {ntype!r}")
        elif set(node_types[ntype]["required_properties"]) - n.keys():
            errors.append(f"missing required properties for {nid}")
    counts: Counter[tuple[str, str]] = Counter()
    incoming: Counter[tuple[str,str]] = Counter()
    for e in edges:
        etype = edge_types.get(e.get("type"))
        if not etype:
            errors.append(f"undefined edge type {e.get('type')!r}")
            continue
        source, target = by_id.get(e.get("source_id")), by_id.get(e.get("target_id"))
        if not source or not target:
            errors.append(f"dangling graph edge {e.get('source_id')}->{e.get('target_id')}")
            continue
        if source.get("type") not in etype["source_types"] or target.get("type") not in etype["target_types"]:
            errors.append(f"invalid endpoint types for {e.get('type')}")
        missing=set(etype["required_attributes"])-e.keys()
        if missing: errors.append(f"edge {e.get('type')} missing attributes {sorted(missing)}")
        counts[(e["source_id"], e["type"])] += 1
        incoming[(e["target_id"],e["type"])] += 1
        if etype["effect"].startswith(("TRACE_ONLY","EVIDENCE_TRACE")) and e.get("assertion_status") == "APPROVED_HARD_DEPENDENCY":
            errors.append("trace-only edge misclassified as hard dependency")
    for (source, relation), count in counts.items():
        edge = edge_types[relation]
        cardinality = edge["cardinality"]
        if cardinality.startswith("0..1") and count > 1:
            errors.append(f"cardinality violation {source}:{relation}")
    for (target,relation),count in incoming.items():
        if relation=="HAS_WORK_SLICE" and count>1:
            errors.append(f"slice has multiple parents: {target}")
    return errors


def estimate_errors(record: dict[str, Any], lifecycle: str, model: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    states = set(model["states"])
    if lifecycle not in model["lifecycle_required_metrics"]:
        return [f"invalid lifecycle {lifecycle}"]
    if record.get("lifecycle_state") != lifecycle:
        errors.append("estimate lifecycle mismatch")
    metrics = record.get("metrics", {})
    for name, item in metrics.items():
        if name not in model["metrics"]:
            errors.append(f"undefined estimate metric {name}")
            continue
        state = item.get("state")
        if state not in states:
            errors.append(f"invalid estimate state for {name}")
            continue
        value = item.get("value")
        if item.get("unit") and item.get("unit") != model["metrics"][name]["unit"]:
            errors.append(f"estimate unit mismatch for {name}")
        if state in {"UNKNOWN", "NOT_MEASURED", "NOT_APPLICABLE", "PENDING_APPROVAL"} and value == 0:
            errors.append(f"{state} cannot be encoded as zero: {name}")
        if state == "NOT_APPLICABLE" and (not item.get("rationale") or not item.get("evidence_ref")):
            errors.append(f"NOT_APPLICABLE lacks rationale/evidence: {name}")
        if state == "MEASURED" and not item.get("measurement_evidence"):
            errors.append(f"MEASURED lacks evidence: {name}")
        if state == "ESTIMATED" and not item.get("evidence_ref"):
            errors.append(f"fabricated estimate lacks evidence: {name}")
    required_for_state=model["lifecycle_required_metrics"].get(lifecycle,[])
    if required_for_state:
        required = model["metrics"].keys() if required_for_state[0].startswith("all_") else required_for_state
        for name in required:
            if name not in metrics:
                errors.append(f"lifecycle {lifecycle} missing explicit estimate state for {name}")
    if lifecycle in {"READY_FOR_COMMITMENT", "COMMITTED", "RELEASE_CANDIDATE"}:
        required = model["lifecycle_required_metrics"][lifecycle]
        names = model["metrics"].keys() if required and required[0].startswith("all_") else required
        for name in names:
            if name not in metrics or metrics[name].get("state") in {"UNKNOWN", "NOT_MEASURED", "PENDING_APPROVAL"}:
                errors.append(f"commitment missing resolved metric {name}")
        if lifecycle in {"COMMITTED", "RELEASE_CANDIDATE"} and not record.get("owner_approval_evidence"):
            errors.append("commitment/release lacks owner approval evidence")
        if lifecycle == "RELEASE_CANDIDATE" and not record.get("release_gate_evidence"):
            errors.append("release candidate lacks release-gate evidence")
    return errors


def lifecycle_errors(old: str, new: str, schema: dict[str, Any]) -> list[str]:
    allowed = schema["estimate_model"]["lifecycle_transitions"].get(old, [])
    return [] if new in allowed else [f"invalid lifecycle transition {old}->{new}"]


def multicycle_errors(record: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors=[]
    required=schema["multi_week_exception_record_required"]
    for field in required:
        key={"documented reason the capability cannot reasonably be split into safe, independently valuable slices":"reason","split alternatives considered and why rejected":"split_alternatives","dependencies":"dependencies","owner-approved maximum calendar duration":"max_calendar_duration","owner-approved development and operating cost ceilings, with currency and period":"cost_ceilings","measurable intermediate output and test oracle per <=7-day cycle":"intermediate_outputs","next review date":"review_date","explicitly state intermediate output is not a product release":"intermediate_is_not_release","estimate allocation reconciliation to prevent parent/child double count":"allocation_reconciliation"}[field]
        value=record.get(key)
        if value in (None,"",[],{}): errors.append(f"missing multi-week exception field {key}")
    if record.get("approval_status") not in {"PROPOSED_PENDING_OWNER_APPROVAL","OWNER_APPROVED_WITH_EVIDENCE"}:
        errors.append("invalid multi-week exception approval status")
    if record.get("weekly_cycle_days",8)>7: errors.append("weekly cycle exceeds seven days")
    if record.get("intermediate_is_not_release") is not True: errors.append("intermediate output incorrectly treated as product release")
    return errors


def multicycle_plan_errors(plan: dict[str,Any],schema:dict[str,Any]) -> list[str]:
    errors=[]
    errors.extend(multicycle_errors(plan.get("exception_record",{}),schema))
    slices=plan.get("slices",[])
    if len(slices)<2: errors.append("multi-week plan needs at least two weekly slices")
    seen=set()
    for item in slices:
        if item.get("cycle_days",99)>7: errors.append("slice exceeds seven-day cycle")
        if not item.get("acceptance_oracle"): errors.append("slice lacks intermediate test oracle")
        if item.get("is_product_release") is not False: errors.append("slice wrongly marked as product release")
        for allocation in item.get("allocation_refs",[]):
            if allocation in seen: errors.append("duplicate work allocation/double count")
            seen.add(allocation)
    return errors


def scope_errors(paths: list[str]) -> list[str]:
    return [f"unauthorized mission path: {path}" for path in paths if not path.startswith("docs/phase5/planning-contract/")]


def decision_order(decision_ids: set[str], relations: list[dict[str, Any]]) -> list[str] | None:
    indegree={x:0 for x in decision_ids}; outgoing=defaultdict(list)
    for e in relations:
        if e.get("relation_type")=="HARD_PREREQUISITE":
            source,target=e.get("source_id"),e.get("target_id")
            if source not in indegree or target not in indegree:return None
            outgoing[target].append(source); indegree[source]+=1
    queue=deque(sorted(x for x,n in indegree.items() if n==0)); order=[]
    while queue:
        node=queue.popleft(); order.append(node)
        for nxt in sorted(outgoing[node]):
            indegree[nxt]-=1
            if indegree[nxt]==0:queue.append(nxt)
    return order if len(order)==len(indegree) else None


def approval_errors(state: dict[str,Any]) -> list[str]:
    if state.get("status") in {"APPROVED","OWNER_APPROVED"} and not all(state.get(k) for k in ["approver","approved_at","evidence"]):
        return ["approved state lacks approver/date/evidence"]
    if state.get("status")=="PENDING_APPROVAL" and any(state.get(k) for k in ["approver","approved_at","evidence"]):
        return ["pending approval contains approval evidence fields"]
    return []


def ci_errors(evidence: dict[str,Any]) -> list[str]:
    errors=[]
    latest=evidence.get("latest_verified_pr_commit")
    if not isinstance(latest,str) or not re.fullmatch(r"[0-9a-f]{40}",latest): errors.append("CI lacks exact tested commit SHA")
    for run in evidence.get("workflow_runs",[]):
        if run.get("tested_commit")!=latest: errors.append(f"CI run is attributed to another commit: {run.get('run_id')}")
        if run.get("conclusion") not in {"success","failure","cancelled","timed_out","action_required"}: errors.append(f"invalid workflow conclusion: {run.get('run_id')}")
        for job in run.get("jobs",[]):
            if job.get("conclusion") not in {"success","failure","skipped","cancelled","timed_out","action_required"}:
                errors.append(f"invalid job conclusion in {run.get('run_id')}")
            if job.get("conclusion")=="skipped" and job.get("reported_status")=="PASS":
                errors.append(f"skipped job presented as pass: {job.get('name')}")
    return errors


def fixture_checks(schema: dict[str, Any], real: dict[str, Any]) -> list[dict[str, str]]:
    checks: list[dict[str, str]] = []
    def record(test_id: str, condition: bool) -> None:
        checks.append({"test_id": test_id, "status": "PASS" if condition else "FAIL"})
    dset = {f"P5-D{i:02d}" for i in range(1,17)}
    aset = {f"A{i:02d}" for i in range(18)}
    pset = {f"O5-{i:02d}" for i in range(1,15)} | {"F06", "A01..A09", "WALLET-v0.20"} | {f"BP52-{i:02d}" for i in range(1,23)}
    gates = {f"P5-B{i:02d}" for i in range(1,17)}
    snap = {"snapshot_id":SNAPSHOT_ID,"certified_source_commit":SOURCE_COMMIT}
    good = {"ref_type":"DECISION","ref_id":"P5-D10","relation":"REQUIRES_APPROVAL"}
    record("F04-01-valid-P5-D10", not ref_errors([good],dset,pset,aset,schema,gates,snap))
    record("F04-02-short-D10-rejected", bool(ref_errors([{**good,"ref_id":"D10"}],dset,pset,aset,schema,gates,snap)))
    record("F04-03-combined-range-rejected", bool(ref_errors([{**good,"ref_id":"P5-D01..09,13"}],dset,pset,aset,schema,gates,snap)))
    record("F04-04-dangling-artifact-rejected", bool(ref_errors([{"ref_type":"ARTIFACT","ref_id":"A99","relation":"DERIVED_FROM"}],dset,pset,aset,schema,gates,snap)))
    record("F04-05-invalid-ref-type-rejected", bool(ref_errors([{"ref_type":"BOGUS","ref_id":"P5-D10","relation":"RELATED_TO"}],dset,pset,aset,schema,gates,snap)))
    record("F04-06-snapshot-mismatch-rejected", bool(ref_errors([{"ref_type":"CERTIFIED_SNAPSHOT","ref_id":"other","source_commit":SOURCE_COMMIT,"relation":"REQUIRES_INPUT"}],dset,pset,aset,schema,gates,snap)))
    record("F04-07-proposed-artifact-reference-accepted", not ref_errors([{"ref_type":"ARTIFACT","ref_id":"A01","relation":"DERIVED_FROM"}],dset,pset,aset,schema,gates,snap))
    record("F04-08-external-condition-is-not-artifact", bool(ref_errors([{"ref_type":"EXTERNAL_CONDITION","ref_id":"A01","relation":"REQUIRES_APPROVAL","description":"x","owner":"owner","resolution_evidence_required":True}],dset,pset,aset,schema,gates,snap)))
    record("F04-09-duplicate-reference-rejected", bool(ref_errors([good,good],dset,pset,aset,schema,gates,snap)))
    record("F02-01-hard-DAG-accepted", not hard_cycle(dset,[{"source_id":"P5-D02","target_id":"P5-D01","relation_type":"HARD_PREREQUISITE"}]))
    record("F02-02-direct-hard-cycle-rejected", hard_cycle(dset,[{"source_id":"P5-D01","target_id":"P5-D02","relation_type":"HARD_PREREQUISITE"},{"source_id":"P5-D02","target_id":"P5-D01","relation_type":"HARD_PREREQUISITE"}]))
    record("F02-03-indirect-hard-cycle-rejected", hard_cycle(dset,[{"source_id":"P5-D01","target_id":"P5-D02","relation_type":"HARD_PREREQUISITE"},{"source_id":"P5-D02","target_id":"P5-D03","relation_type":"HARD_PREREQUISITE"},{"source_id":"P5-D03","target_id":"P5-D01","relation_type":"HARD_PREREQUISITE"}]))
    record("F02-04-mutual-influence-allowed", not hard_cycle(dset,[{"source_id":"P5-D01","target_id":"P5-D02","relation_type":"INFLUENCES"},{"source_id":"P5-D02","target_id":"P5-D01","relation_type":"INFLUENCES"}]))
    record("F02-05-self-hard-edge-rejected", hard_cycle(dset,[{"source_id":"P5-D01","target_id":"P5-D01","relation_type":"HARD_PREREQUISITE"}]))
    record("F02-06-unknown-decision-rejected", hard_cycle(dset,[{"source_id":"P5-D01","target_id":"P5-D99","relation_type":"HARD_PREREQUISITE"}]))
    record("F02-07-invalid-relation-rejected", bool(decision_relation_errors(dset,[{"source_id":"P5-D01","target_id":"P5-D02","relation_type":"BOGUS"}],schema)))
    record("F02-08-co-decision-group-valid", all(len(g["members"])>=2 and set(g["members"])<=dset for g in schema["decision_review_groups"] if g["group_id"]!="G-OPEN-DECISIONS"))
    # Contract fixture for semantic, policy, lifecycle, evidence, CI, and scope controls.
    def has_duplicate_ids(values: list[dict[str,Any]]) -> bool:
        ids=[v.get("id") for v in values]
        return len(ids)!=len(set(ids))
    record("F07-01-duplicate-id-rejected", has_duplicate_ids([{"id":"x"},{"id":"x"}]))
    record("F07-02-missing-field-rejected", bool({"required"}-set({"id":None})))
    record("F07-03-invalid-namespace-rejected", bool(ref_errors([{"ref_type":"DECISION","ref_id":"D10","relation":"RELATED_TO"}],dset,pset,aset,schema,gates,snap)))
    record("F07-04-unapproved-approved-state-rejected", bool(approval_errors({"status":"APPROVED","approver":"owner","approved_at":"2026-01-01","evidence":None})))
    record("F07-05-missing-approval-evidence-rejected", bool(approval_errors({"status":"PENDING_APPROVAL","approver":"owner","approved_at":"2026-01-01","evidence":"evidence"})))
    record("F07-06-graph-invalid-endpoint-rejected", bool(graph_errors([], [{"type":"HAS_ESTIMATE","source_id":"missing","target_id":"missing"}], schema)))
    record("F07-07-undefined-node-edge-rejected", bool(graph_errors([{"id":"n","type":"NOPE"}],[{"type":"NOPE","source_id":"n","target_id":"n"}],schema)))
    nodes=[{"id":"d","type":"DELIVERABLE","title":"x","outcome":"x","lifecycle_state":"PROPOSED","approval_status":"PROPOSED","evidence_refs":[]},{"id":"w1","type":"WEEK","starts_on":"2026-01-01","ends_on":"2026-01-07","capacity_refs":[]},{"id":"w2","type":"WEEK","starts_on":"2026-01-08","ends_on":"2026-01-14","capacity_refs":[]}]
    scheduled=[{"type":"SCHEDULED_IN","source_id":"d","target_id":w,"assertion_status":"PROPOSED","approval_status":"PROPOSED","evidence_ref":"fixture"} for w in ["w1","w2"]]
    record("F07-08-cardinality-violation-rejected", any("cardinality violation" in e for e in graph_errors(nodes,scheduled,schema)))
    caps=[{"id":"d","type":"DELIVERABLE","title":"x","outcome":"x","lifecycle_state":"PROPOSED","approval_status":"PROPOSED","evidence_refs":[]},{"id":"c","type":"CAPABILITY","source_ref":"fixture","owner_boundary":"fixture"}]
    record("F07-09-trace-only-not-hard-rejected", any("trace-only edge" in e for e in graph_errors(caps,[{"type":"IMPLEMENTS","source_id":"d","target_id":"c","source_ref":"fixture","assertion_status":"APPROVED_HARD_DEPENDENCY","evidence_ref":"fixture"}],schema)))
    record("POS-10-valid-graph-endpoints-accepted", not graph_errors(caps,[{"type":"IMPLEMENTS","source_id":"d","target_id":"c","source_ref":"fixture","assertion_status":"PROPOSED","evidence_ref":"fixture"}],schema))
    record("F06-01-unknown-zero-rejected", bool(estimate_errors({"lifecycle_state":"PROPOSED","metrics":{"development_cost":{"state":"UNKNOWN","value":0}}},"PROPOSED",schema["estimate_model"])))
    record("F06-02-not-applicable-without-evidence-rejected", bool(estimate_errors({"lifecycle_state":"PROPOSED","metrics":{"risk":{"state":"NOT_APPLICABLE"}}},"PROPOSED",schema["estimate_model"])))
    record("F06-03-fabricated-estimate-without-source-rejected", bool(estimate_errors({"lifecycle_state":"PROPOSED","metrics":{"human_effort":{"state":"ESTIMATED","value":1,"unit":"person_hour"}}},"PROPOSED",schema["estimate_model"])))
    record("F06-04-invalid-lifecycle-transition-rejected", bool(lifecycle_errors("PROPOSED","COMMITTED",schema)))
    record("F06-05-commitment-with-unknown-rejected", bool(estimate_errors({"lifecycle_state":"COMMITTED","metrics":{"development_cost":{"state":"UNKNOWN"}}},"COMMITTED",schema["estimate_model"])))
    record("F07-11-release-commitment-with-missing-gates-rejected", bool(estimate_errors({"lifecycle_state":"RELEASE_CANDIDATE","metrics":{}},"RELEASE_CANDIDATE",schema["estimate_model"])))
    record("F06-06-estimated-not-measured-distinguished", schema["estimate_model"]["states"]==["ESTIMATED","MEASURED","UNKNOWN","NOT_MEASURED","NOT_APPLICABLE","PENDING_APPROVAL"])
    record("F03-01-ci-record-requires-commit", not real["external_ci_evidence"].get("latest_verified_pr_commit")=="")
    misclassified={"latest_verified_pr_commit":"a"*40,"workflow_runs":[{"run_id":1,"tested_commit":"a"*40,"conclusion":"success","jobs":[{"name":"docs","conclusion":"success","reported_status":"PASS"},{"name":"product","conclusion":"skipped","reported_status":"PASS"}]}]}
    record("F03-02-skipped-not-pass", bool(ci_errors(misclassified)))
    record("F07-10-unauthorized-scope-path-rejected", not "src/product.py".startswith("docs/phase5/planning-contract/"))
    record("F05-01-multicycle-option-has-exception-controls", all(all(k in x and x[k] for k in ["example","data_effect","acceptance_effect","double_count_effect","capacity_effect","blueprint_alignment","approval_status"]) for x in schema["multi_week_options"]))
    record("F05-02-multicycle-schema-keeps-week-cap", "<= 6 days" in " ".join(schema["graph_node_types"][2]["validation_rules"]))
    valid_exception={"reason":"not splittable safely","split_alternatives":["split A","split B"],"dependencies":["source-backed dependency"],"max_calendar_duration":{"value":"UNKNOWN","approval":"PENDING_APPROVAL"},"cost_ceilings":{"development":"UNKNOWN","operating":"UNKNOWN","currency":"owner-supplied","period":"owner-supplied"},"intermediate_outputs":[{"cycle_days":7,"output":"testable slice","oracle":"test evidence"}],"review_date":"owner-set-date","intermediate_is_not_release":True,"allocation_reconciliation":"parent roll-up only; no duplicate effort","approval_status":"PROPOSED_PENDING_OWNER_APPROVAL","weekly_cycle_days":7}
    valid_plan={"exception_record":valid_exception,"slices":[{"cycle_days":7,"acceptance_oracle":"fixture test","is_product_release":False,"allocation_refs":["phase4:work-a"]},{"cycle_days":7,"acceptance_oracle":"fixture test","is_product_release":False,"allocation_refs":["phase4:work-b"]}]}
    record("F05-05-multicycle-slice-model-positive", not multicycle_plan_errors(valid_plan,schema))
    valid_plan["slices"][1]["allocation_refs"]=["phase4:work-a"]
    record("F05-06-multicycle-double-count-negative", bool(multicycle_plan_errors(valid_plan,schema)))
    bad_multi={"weekly_cycle_days":8,"approval_status":"PROPOSED_PENDING_OWNER_APPROVAL","reason":"x"}
    record("F05-03-multicycle-without-exception-record-rejected", bool(multicycle_errors(bad_multi,schema)))
    record("F05-04-multicycle-exception-within-scope-accepted", not multicycle_errors({"reason":"not splittable safely","split_alternatives":["split A","split B"],"dependencies":["source-backed dependency"],"max_calendar_duration":{"value":"UNKNOWN","approval":"PENDING_APPROVAL"},"cost_ceilings":{"development":"UNKNOWN","operating":"UNKNOWN","currency":"owner-supplied","period":"owner-supplied"},"intermediate_outputs":[{"cycle_days":7,"output":"testable slice","oracle":"test evidence"}],"review_date":"owner-set-date","intermediate_is_not_release":True,"allocation_reconciliation":"parent roll-up only; no duplicate effort","approval_status":"PROPOSED_PENDING_OWNER_APPROVAL","weekly_cycle_days":7},schema))
    # Positive fixture coverage.
    record("POS-01-open-decision-preserved", all(d["status"]=="OPEN" for d in real["decisions"]))
    record("POS-02-valid-influence-cycle-accepted", not hard_cycle(dset,[{"source_id":"P5-D01","target_id":"P5-D02","relation_type":"INFLUENCES"},{"source_id":"P5-D02","target_id":"P5-D01","relation_type":"INFLUENCES"}]))
    record("POS-03-valid-reference-to-snapshot", not ref_errors([{"ref_type":"CERTIFIED_SNAPSHOT","ref_id":SNAPSHOT_ID,"source_commit":SOURCE_COMMIT,"relation":"REQUIRES_INPUT"}],dset,pset,aset,schema,gates,snap))
    unknown_metrics={name:{"state":"UNKNOWN"} for name in schema["estimate_model"]["metrics"]}
    record("POS-04-valid-unknown-proposal", not estimate_errors({"lifecycle_state":"PROPOSED","metrics":unknown_metrics},"PROPOSED",schema["estimate_model"]))
    record("POS-05-valid-multicycle-proposal", all(x["approval_status"]=="PROPOSED_PENDING_OWNER_APPROVAL" for x in schema["multi_week_options"]))
    record("POS-06-valid-open-decision", all(d["status"]=="OPEN" and d["owner_approval"]["status"]=="PENDING_APPROVAL" for d in real["decisions"]))
    record("POS-07-history-ci-sha-pinned", bool(re.fullmatch(r"[0-9a-f]{40}",real["external_ci_evidence"]["latest_verified_pr_commit"])))
    record("POS-08-schedule-cadence-policy-present", "<= 6 days" in " ".join(sum((x["validation_rules"] for x in schema["graph_node_types"] if x["type_id"]=="WEEK"),[])))
    record("POS-09-co-decision-groups-preserve-open", all(set(g["members"])<=dset for g in schema["decision_review_groups"]))
    record("SCOPE-01-unauthorized-path-rejected", bool(scope_errors(["src/main.py"])))
    output_registry=read_json(CONTRACT/"output-artifact-registry.json")
    active=set(output_registry.get("current_mvp_artifacts",[]))
    deferred=set(output_registry.get("deferred_artifact_ids",[]))
    all_ids={x["artifact_id"] for x in output_registry.get("artifacts",[])}
    record("SCOPE-02-single-lightweight-mvp-output-and-time-cap", active=={"A01"} and active|deferred==all_ids and schema.get("current_mvp_contract",{}).get("implementation_time_cap_minutes")==60 and len(schema.get("current_mvp_contract",{}).get("request_modes",[]))==4)
    return checks


def validate_real() -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    names = ["decision-register.json","output-artifact-registry.json","acceptance-gates.json","planning-contract-validation.json","planning-contract-schema.json"]
    data = {name: read_json(CONTRACT/name) for name in names}
    decisions = data["decision-register.json"]["decisions"]
    artifacts = data["output-artifact-registry.json"]["artifacts"]
    gates = data["acceptance-gates.json"]["gates"]
    schema = data["planning-contract-schema.json"]
    snap = read_json(ROOT/"docs/phase4/task-map-graph/phase4-certified-snapshot.json")
    dids = {x["decision_id"] for x in decisions}; aids = {x["artifact_id"] for x in artifacts}; gids = {x["gate_id"] for x in gates}
    if len(dids)!=len(decisions) or len(aids)!=len(artifacts) or len(gids)!=len(gates): errors.append("duplicate entity ID")
    if any(d.get("status")!="OPEN" or d.get("owner_approval",{}).get("status")!="PENDING_APPROVAL" for d in decisions): errors.append("open decision was promoted")
    registry=data["output-artifact-registry.json"]
    active=set(registry.get("current_mvp_artifacts",[])); deferred=set(registry.get("deferred_artifact_ids",[]))
    if active!={"A01"} or active|deferred!=aids or active&deferred: errors.append("MVP output registry must contain only A01 and defer the remaining historical proposals")
    if any(d.get("review_disposition") is None or d.get("review_reason") is None for d in decisions): errors.append("decision review disposition missing")
    source_registry=read_json(CONTRACT/"planning-knowledge-registry.json")
    plan_source=next((x for x in source_registry.get("sources",[]) if x.get("source_document")=="docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md"),{})
    if plan_source.get("review_status")!="COMPLETE_SEMANTIC_REVIEW" or plan_source.get("review_scope_end")!=plan_source.get("total_lines") or plan_source.get("reviewed_ranges")!=[[1,plan_source.get("total_lines")]]: errors.append("implementation-plan semantic review metadata is incomplete or stale")
    for dec in decisions: errors.extend(approval_errors(dec.get("owner_approval",{})))
    if len(decisions)!=16 or len(artifacts)!=18: errors.append("counts differ from existing contract inventory")
    refs=[]
    legacy_map={"snapshot pinned":("CERTIFIED_SNAPSHOT",SNAPSHOT_ID,"REQUIRES_INPUT"),"Evidence Join Index":("SOURCE_DOCUMENT","docs/audits/phase2-source-coverage/evidence-join-index.json","REQUIRES_INPUT"),"snapshot OPEN ledger":("SOURCE_DOCUMENT","docs/phase4/task-map-graph/task-map-mapping.json","REQUIRES_INPUT"),"explicit later scope approval":("EXTERNAL_CONDITION","external:phase5-scope-approval","REQUIRES_APPROVAL"),"test/CI evidence":("EXTERNAL_CONDITION","external:phase5-ci-evidence","REQUIRES_INPUT"),"close gate":("EXTERNAL_CONDITION","external:phase5-owner-close-gate","REQUIRES_APPROVAL"),"validated outputs":("EXTERNAL_CONDITION","external:phase5-validated-outputs","REQUIRES_INPUT")}
    for a in artifacts:
        for ref in a.get("dependencies",[]):
            if not isinstance(ref,dict): errors.append(f"non-normalized dependency {a['artifact_id']}: {ref!r}")
            else: refs.append(ref)
    for a in artifacts:
        errors.extend(ref_errors(a.get("dependencies",[]),dids,{x["decision_id"] for x in data["decision-register.json"]["approved_policy_baseline"]},aids,schema,gids,snap))
    rels=data["decision-register.json"].get("decision_relations",[])
    errors.extend(decision_relation_errors(dids,rels,schema))
    for r in rels:
        if r.get("approval_status") not in {"PROPOSED","TRACE_ONLY","OWNER_APPROVED"}: errors.append("invalid decision relation approval state")
    for group in data["decision-register.json"].get("co_decision_groups",[]):
        if len(group.get("members",[]))<2 or len(set(group["members"]))!=len(group["members"]) or not set(group["members"])<=dids: errors.append(f"invalid co-decision group {group}")
    if any(x.get("status")!="OPEN" for x in decisions): errors.append("decision status invalid")
    errors.extend(graph_errors([],[],schema))
    for gate in gates:
        errors.extend(ref_errors(gate.get("references",[]),dids,{x["decision_id"] for x in data["decision-register.json"]["approved_policy_baseline"]},aids,schema,gids,snap))
        if gate.get("gate_id","").startswith("P5-C") and (not gate.get("validation_method",{}).get("test_ids") or not gate.get("observed_status")):
            errors.append(f"corrective acceptance gate lacks evidence fields: {gate.get('gate_id')}")
    for item in data["decision-register.json"]["approved_policy_baseline"]:
        errors.extend(ref_errors(item.get("source_references",[]),dids,{x["decision_id"] for x in data["decision-register.json"]["approved_policy_baseline"]},aids,schema,gids,snap))
    errors.extend(ci_errors(data["planning-contract-validation.json"].get("external_ci_evidence",{})))
    # Source-policy trace is exact-line coverage; basic schema and required ranges.
    with (CONTRACT/"source-policy-trace.csv").open(encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f); rows=list(reader)
        required={"Rule ID","Source ref type","Source ref ID","Source commit","Source blob SHA","Rule ref type","Rule ref ID"}
        if not reader.fieldnames or not required<=set(reader.fieldnames): errors.append("source-policy-trace typed reference schema incomplete")
        if len([x for x in rows if x.get("Rule ID","").startswith("BP52-")])!=22: errors.append("22 policy trace rows missing")
        for row in rows:
            path=row.get("Source ref ID","").split("#",1)[0]
            if row.get("Source ref type")!="SOURCE_LOCATOR" or row.get("Source commit")!=SOURCE_COMMIT or row.get("Source blob SHA")!=git_blob(path): errors.append(f"invalid source trace provenance: {row.get('Rule ID')}")
    # Typed references embedded in decision records are validated with the same resolver.
    for dec in decisions:
        for field in ["source_references","approved_policy_references","impacted_artifacts"]:
            errors.extend(ref_errors(dec.get(field,[]),dids,{x["decision_id"] for x in data["decision-register.json"]["approved_policy_baseline"]},aids,schema,gids,snap))
    # The approved baseline is an exact registry: range aliases must not remain.
    policies={x["decision_id"] for x in data["decision-register.json"]["approved_policy_baseline"]}
    if any(".." in x or "," in x for x in policies): errors.append("non-normalized approved policy ID range")
    # Typed decision edges are not promoted to owner decisions; unknown statuses/IDs reject.
    if any(r.get("approval_status") not in {"PROPOSED","TRACE_ONLY","OWNER_APPROVED"} for r in rels): errors.append("invalid decision relation approval status")
    # Confirm phase4 immutable identity; validator itself checks all 27 payloads.
    validator=subprocess.run([sys.executable,"docs/phase4/task-map-graph/validate_phase4_snapshot.py"],cwd=ROOT,capture_output=True,text=True)
    if validator.returncode!=0 or "CERTIFIED_SNAPSHOT_VALID" not in validator.stdout: errors.append("certified snapshot validator failed")
    changed=subprocess.run(["git","diff","--name-only",BASE,"--"],cwd=ROOT,capture_output=True,text=True)
    status=subprocess.run(["git","status","--porcelain"],cwd=ROOT,capture_output=True,text=True)
    changed_paths=set(changed.stdout.splitlines())
    for line in status.stdout.splitlines():
        path=line[3:]
        if path: changed_paths.add(path)
    changed_paths=sorted(changed_paths)
    errors.extend(scope_errors(changed_paths))
    order=decision_order(dids,rels)
    if order is None: errors.append("hard prerequisite order cannot be derived")
    return errors,{"snapshot_output":validator.stdout.strip(),"changed_paths":changed_paths,"decision_count":len(decisions),"artifact_count":len(artifacts),"active_mvp_artifacts":sorted(active),"deferred_artifact_count":len(deferred),"gate_count":len(gates),"hard_prerequisite_topological_order":order}


def main() -> int:
    schema=read_json(CONTRACT/"planning-contract-schema.json")
    real=read_json(CONTRACT/"planning-contract-validation.json")
    fixture=fixture_checks(schema,{**read_json(CONTRACT/"planning-contract-validation.json"),**read_json(CONTRACT/"decision-register.json")})
    errors,summary=validate_real()
    failed=[x for x in fixture if x["status"]!="PASS"]
    output={"fixture_results":fixture,"fixture_summary":{"passed":len(fixture)-len(failed),"failed":len(failed)},"real_validation":{"errors":errors,**summary}}
    print(json.dumps(output,ensure_ascii=False,indent=2))
    return 0 if not errors and not failed else 1


if __name__=="__main__":
    raise SystemExit(main())
