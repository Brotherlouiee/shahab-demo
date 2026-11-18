#!/usr/bin/env python3
"""Append Graphify extraction records to a directed multigraph without rebuild.

Unlike graphify.build_from_json/build_merge, never coalesce edges by endpoints,
discard isolated nodes, or replace old records by source_file. New input content
hashes make replays idempotent; an input name reused with different bytes fails.
The output must be a new path; originals are never overwritten.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import tempfile
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record_digest(record: dict) -> str:
    """Hash the exact JSON value, independent of dictionary field ordering."""
    encoded = json.dumps(record, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def edge_identity(edge: dict) -> tuple:
    return (edge.get("source"), edge.get("target"), edge.get("relation"))


def load(path: Path) -> dict:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError(f"{path}: expected JSON object")
    return obj


def validate_graph(g: dict) -> None:
    if g.get("directed") is not True or g.get("multigraph") is not True:
        raise ValueError("base must be a directed multigraph; refusing conversion")
    if not all(isinstance(g.get(k), list) for k in ("nodes", "links")):
        raise ValueError("base must contain nodes and links arrays")
    ids = set()
    for n in g["nodes"]:
        if not isinstance(n, dict) or not isinstance(n.get("id"), str) or not n["id"]:
            raise ValueError("all node ids must be nonempty strings")
        if n["id"] in ids:
            raise ValueError(f"duplicate node id: {n['id']}")
        ids.add(n["id"])
    explicit_keys = set()
    keyed_pairs = set()
    unkeyed_pairs = set()
    for e in g["links"]:
        if not isinstance(e, dict) or e.get("source") not in ids or e.get("target") not in ids:
            raise ValueError(f"invalid or dangling edge: {e!r}")
        if "key" in e:
            keyed_pairs.add((e["source"], e["target"]))
            try:
                k = (e["source"], e["target"], e["key"])
                if k in explicit_keys:
                    raise ValueError(f"duplicate multigraph edge key: {k!r}")
                explicit_keys.add(k)
            except TypeError as exc:
                raise ValueError("unhashable multigraph edge key") from exc
        else:
            unkeyed_pairs.add((e["source"], e["target"]))
    # NetworkX auto-assigns unkeyed edges integer keys: if mixed with explicit
    # keys for one pair an explicit key can overwrite an auto-generated key.
    if keyed_pairs & unkeyed_pairs:
        raise ValueError("mixed keyed and unkeyed edges for same endpoints can collapse")
    for h in g.get("hyperedges", []):
        members = h.get("nodes", []) if isinstance(h, dict) else []
        if not isinstance(members, list) or any(member not in ids for member in members):
            raise ValueError(f"invalid hyperedge: {h!r}")


def union(base: dict, additions: list[tuple[str, str, dict]]) -> dict:
    """Return a new graph. Repeated node IDs keep full incoming records as variants.

    Every input edge/hyperedge remains a separate full record, even exact
    duplicates. Replaying an identical input name and SHA is a no-op; changing
    bytes under an already processed name raises rather than silently replacing.
    """
    validate_graph(base)
    out = copy.deepcopy(base)
    out.setdefault("hyperedges", [])
    provenance = out.setdefault("lossless_merge", {})
    applied = provenance.setdefault("inputs", [])
    variants = provenance.setdefault("node_variants", [])
    quarantined = provenance.setdefault("quarantined_edges", [])
    provenance.setdefault("protected_base_link_count", len(base["links"]))
    if not isinstance(applied, list) or not isinstance(variants, list) or not isinstance(quarantined, list):
        raise ValueError("invalid lossless_merge metadata")
    known = {x["name"]: x["sha256"] for x in applied}
    prohibited = {x["record_sha256"] for x in quarantined}
    quarantined_by_identity = {}
    for item in quarantined:
        quarantined_by_identity.setdefault(edge_identity(item["original_edge"]), []).append(item)
    ids = {n["id"] for n in out["nodes"]}
    for name, sha256, data in additions:
        if not name or "/" in name or "\\" in name:
            raise ValueError("input names must be portable basenames")
        if name in known:
            if known[name] == sha256:
                continue
            raise ValueError(f"input {name} was already applied with different SHA-256")
        nodes, edges, hypers = data.get("nodes", []), data.get("edges", data.get("links", [])), data.get("hyperedges", [])
        if not all(isinstance(x, list) for x in (nodes, edges, hypers)):
            raise ValueError(f"{name}: nodes, edges and hyperedges must be arrays")
        for edge in edges:
            edge_hash = record_digest(edge)
            if edge_hash in prohibited:
                raise ValueError(f"{name}: input attempts to reintroduce a quarantined edge")
            if edge_identity(edge) in quarantined_by_identity:
                allowed = {h for item in quarantined_by_identity[edge_identity(edge)] for h in item.get("allowed_replacement_sha256", [])}
                if edge_hash not in allowed:
                    raise ValueError(f"{name}: same quarantined relationship with changed metadata; explicit replacement hash required")
        for node in nodes:
            if not isinstance(node, dict) or not isinstance(node.get("id"), str) or not node["id"]:
                raise ValueError(f"{name}: invalid node")
            if node["id"] in ids:
                variants.append({"input": name, "input_sha256": sha256, "node": copy.deepcopy(node)})
            else:
                out["nodes"].append(copy.deepcopy(node))
                ids.add(node["id"])
        out["links"].extend(copy.deepcopy(edges))
        out["hyperedges"].extend(copy.deepcopy(hypers))
        applied.append({"name": name, "sha256": sha256, "node_records": len(nodes), "edge_records": len(edges), "hyperedge_records": len(hypers)})
        known[name] = sha256
    validate_graph(out)
    # Exact prefix checks prevent an implementation change from dropping or
    # rewriting a pre-existing record, including duplicate edges and attributes.
    for field in ("nodes", "links", "hyperedges"):
        old = base.get(field, [])
        if out[field][:len(old)] != old:
            raise AssertionError(f"base {field} changed during union")
    return out


def quarantine_edges(base: dict, corrections: list[dict]) -> dict:
    """Remove explicitly identified invalid semantic edges from active traversal.

    Each exact original JSON record is retained in the graph together with its
    canonical SHA-256, evidence citations and rationale. Reintroduction of the
    exact record by a future new input is rejected. Structural baseline records
    are protected; duplicate-identical candidates fail instead of guessing.
    """
    validate_graph(base)
    out = copy.deepcopy(base)
    meta = out.get("lossless_merge")
    if not isinstance(meta, dict) or not isinstance(meta.get("protected_base_link_count"), int):
        raise ValueError("missing protected structural baseline metadata")
    history = meta.setdefault("quarantined_edges", [])
    protected_count = meta["protected_base_link_count"]
    if not 0 <= protected_count <= len(out["links"]):
        raise ValueError("invalid protected structural baseline length")
    for correction in corrections:
        if not isinstance(correction, dict):
            raise ValueError("corrections must be objects")
        wanted = correction.get("record_sha256")
        reason = correction.get("reason")
        evidence = correction.get("evidence")
        allowed = correction.get("allowed_replacement_sha256", [])
        if not isinstance(wanted, str) or len(wanted) != 64 or not isinstance(reason, str) or not reason.strip() or not isinstance(evidence, list) or not evidence:
            raise ValueError("each quarantine needs record_sha256, reason and evidence")
        if not isinstance(allowed, list) or any(not isinstance(x, str) or len(x) != 64 for x in allowed):
            raise ValueError("allowed_replacement_sha256 must be an array of hashes")
        matches = [i for i, edge in enumerate(out["links"]) if record_digest(edge) == wanted]
        if len(matches) != 1:
            raise ValueError(f"expected exactly one edge for quarantine, got {len(matches)}")
        index = matches[0]
        if index < protected_count:
            raise ValueError("refusing to quarantine a protected structural edge")
        old = out["links"].pop(index)
        history.append({"record_sha256": wanted, "original_edge": old, "reason": reason, "evidence": copy.deepcopy(evidence), "allowed_replacement_sha256": list(allowed), "action": "quarantined_from_active_graph"})
    for entry in history:
        original = entry["original_edge"]
        for active in out["links"][protected_count:]:
            if edge_identity(active) == edge_identity(original) and record_digest(active) not in entry.get("allowed_replacement_sha256", []):
                raise ValueError("active relationship duplicates quarantined identity without approved replacement hash")
    validate_graph(out)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, type=Path)
    parser.add_argument("--input", action="append", default=[], type=Path)
    parser.add_argument("--corrections", type=Path, help="JSON object with a quarantine array of exact edge hashes and reasons")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    base = args.base.resolve()
    out = args.out.resolve()
    if out == base or out in [p.resolve() for p in args.input] or (args.corrections and out == args.corrections.resolve()):
        parser.error("output must be distinct from all input paths")
    if out.exists():
        parser.error("output exists; choose a new path rather than overwrite")
    inputs = [(p.name, digest(p), load(p)) for p in args.input]
    result = union(load(base), inputs)
    if args.corrections:
        changes = load(args.corrections).get("quarantine")
        if not isinstance(changes, list):
            parser.error("corrections must contain a quarantine array")
        result = quarantine_edges(result, changes)
    out.parent.mkdir(parents=True, exist_ok=True)
    # atomic publication; never rewrite an existing result
    fd, temp = tempfile.mkstemp(prefix=".lossless-", suffix=".json", dir=out.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(result, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temp, out)  # fails atomically if another writer created output
    finally:
        os.unlink(temp)
    print(json.dumps({"nodes": len(result["nodes"]), "links": len(result["links"]), "hyperedges": len(result.get("hyperedges", [])), "node_variants": len(result["lossless_merge"]["node_variants"]), "quarantined_edges": len(result["lossless_merge"]["quarantined_edges"]), "out": str(out)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
