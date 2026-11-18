#!/usr/bin/env python3
"""Exercise lossless graph recovery inside a disposable independent git clone.

Package layout: structural/graph.json, chunks/GSEM-*.json,
relation-review/*.json, tools/lossless_merge.py. Optional corrections file is
provided relative to the package; no checkout, output, or input is overwritten.
"""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def canon(x):
    return json.dumps(x, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def run(args, cwd=None):
    proc = subprocess.run([str(x) for x in args], cwd=cwd, text=True, capture_output=True)
    if proc.returncode:
        raise RuntimeError(f"command failed ({proc.returncode}): {args!r}\n{proc.stderr}\n{proc.stdout}")
    return proc.stdout


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo", type=Path, required=True, help="local git repository to clone without using an existing worktree")
    p.add_argument("--package", type=Path, required=True, help="staged package directory to copy into fresh checkout")
    p.add_argument("--ref", default="main", help="branch in source repository to clone (default main)")
    p.add_argument("--corrections", help="optional quarantine JSON path relative to package")
    p.add_argument("--graphify", type=Path, help="installed Graphify 0.9.112 executable for query/path/explain")
    p.add_argument("--out", type=Path, help="write result JSON to this previously nonexistent path")
    a = p.parse_args()
    repo, package = a.repo.resolve(), a.package.resolve()
    chunks = sorted((package / "chunks").glob("GSEM-*.json"))
    reviews = sorted((package / "relation-review").glob("*.json"))
    if len(chunks) != 22 or len(reviews) != 3:
        raise ValueError(f"expected 22 chunks and 3 relation reviews, got {len(chunks)} and {len(reviews)}")
    needed = [package / "structural/graph.json", package / "tools/lossless_merge.py", package / "tools/test_lossless_merge.py", *chunks, *reviews]
    if a.corrections:
        if Path(a.corrections).is_absolute() or ".." in Path(a.corrections).parts:
            raise ValueError("corrections must be a package-relative path")
        needed.append(package / a.corrections)
    baseline_hashes = {str(x.relative_to(package)): sha(x) for x in needed}
    with tempfile.TemporaryDirectory(prefix="graphify-recovery-") as tmp:
        checkout = Path(tmp) / "checkout"
        run(["git", "clone", "--quiet", "--no-local", "--branch", a.ref, "--single-branch", str(repo), str(checkout)])
        head = run(["git", "rev-parse", "HEAD"], cwd=checkout).strip()
        target = checkout / "knowledge-graph/phase2-reference-docs"
        shutil.copytree(package, target)
        checkpoint = target / "checkpoints/previous-progress.json"
        if checkpoint.exists():
            source_records = json.loads(checkpoint.read_text()).get("sources", [])
            if len(source_records) != 2:
                raise ValueError("checkpoint must pin both reference sources")
            for source in source_records:
                ref = Path(source["path"])
                if ref.is_absolute() or ".." in ref.parts:
                    raise ValueError("source paths must be relative to checkout")
                assert sha(checkout / ref) == source["sha256"], f"source hash mismatch: {ref}"
        for name, original_hash in baseline_hashes.items():
            assert sha(target / name) == original_hash, f"copied package differs: {name}"
        run([sys.executable, "-m", "unittest", "-v", "test_lossless_merge"], cwd=target / "tools")
        base = target / "structural/graph.json"
        copied_inputs = sorted((target / "chunks").glob("GSEM-*.json")) + sorted((target / "relation-review").glob("*.json"))
        out1 = Path(tmp) / "recovered.json"
        out2 = Path(tmp) / "replayed.json"
        tool = target / "tools/lossless_merge.py"
        args = [sys.executable, tool, "--base", base, "--out", out1]
        for x in copied_inputs:
            args += ["--input", x]
        if a.corrections:
            args += ["--corrections", target / a.corrections]
        run(args)
        replay = [sys.executable, tool, "--base", out1, "--out", out2]
        for x in copied_inputs:
            replay += ["--input", x]
        run(replay)
        assert sha(out1) == sha(out2), "replaying prior chunks changed graph bytes"
        graph = json.loads(out1.read_text()); structural = json.loads(base.read_text())
        assert graph["nodes"][:len(structural["nodes"])] == structural["nodes"], "structural node loss"
        assert graph["links"][:len(structural["links"])] == structural["links"], "structural link loss"
        raw_edges = collections.Counter(canon(x) for x in structural["links"])
        raw_nodes = collections.Counter(canon(x) for x in structural["nodes"])
        for file in copied_inputs:
            data = json.loads(file.read_text())
            raw_nodes.update(canon(x) for x in data.get("nodes", []))
            raw_edges.update(canon(x) for x in data.get("edges", data.get("links", [])))
        observed_nodes = collections.Counter(canon(x) for x in graph["nodes"])
        observed_nodes.update(canon(x["node"]) for x in graph["lossless_merge"]["node_variants"])
        observed_edges = collections.Counter(canon(x) for x in graph["links"])
        observed_edges.update(canon(x["original_edge"]) for x in graph["lossless_merge"]["quarantined_edges"])
        assert observed_nodes == raw_nodes, "one or more original node records or witnesses lost"
        assert observed_edges == raw_edges, "one or more original edge records or witnesses lost"
        if (target / "semantic/graph.json").exists():
            published = json.loads((target / "semantic/graph.json").read_text())
            assert published == graph, "staged final graph differs from reproducible rebuild"
        if a.graphify:
            cli = a.graphify.resolve()
            checks = [
                [cli, "query", "Wallet credit ownership and spend order", "--graph", out1, "--budget", "3000"],
                [cli, "path", "docs_shahab_phase_2_development_blueprint_wallet_source_of_detail", "docs_shahab_digital_wallet_wallet_balance_is_customer_liability_not_revenue", "--graph", out1, "--undirected"],
                [cli, "explain", "docs_shahab_digital_wallet_wallet_balance_is_customer_liability_not_revenue", "--graph", out1],
            ]
            for command in checks:
                output = run(command, cwd=checkout)
                if not output.strip():
                    raise AssertionError(f"Graphify produced no output for {command[1]}")
        for name, original_hash in baseline_hashes.items():
            assert sha(package / name) == original_hash, f"original package changed: {name}"
        result = {"result": "PASS" if a.graphify and checkpoint.exists() else "PARTIAL", "source_checkout_head": head, "source_hashes": "PASS" if checkpoint.exists() else "NOT_RUN", "input_files": len(copied_inputs), "nodes": len(graph["nodes"]), "active_links": len(graph["links"]), "quarantined_links": len(graph["lossless_merge"]["quarantined_edges"]), "node_variants": len(graph["lossless_merge"]["node_variants"]), "recovered_sha256": sha(out1), "replay_sha256": sha(out2), "package_bytes_unchanged": True, "all_original_records_and_witnesses_preserved": True, "unit_tests": "PASS", "graphify_query_path_explain": "PASS" if a.graphify else "NOT_RUN"}
        rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if a.out:
            with a.out.open("x", encoding="utf-8") as f:
                f.write(rendered)
        print(rendered, end="")


if __name__ == "__main__":
    main()
