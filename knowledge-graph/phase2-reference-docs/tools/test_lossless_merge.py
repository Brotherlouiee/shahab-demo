#!/usr/bin/env python3
"""Regression cases for lossless graph union and same-source resume."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from lossless_merge import union, validate_graph, quarantine_edges, record_digest


def base():
    return {"directed": True, "multigraph": True, "graph": {"version": "0.9.112"},
            "nodes": [{"id": "a", "label": "A", "attributes": {"line": 1}},
                      {"id": "b", "label": "B"}, {"id": "isolated", "label": "Isolated"}],
            "links": [{"source": "a", "target": "b", "relation": "references", "source_file": "x.md", "source_location": "L1"},
                      {"source": "a", "target": "b", "relation": "references", "source_file": "x.md", "source_location": "L2"}],
            "hyperedges": []}


class LosslessMergeTest(unittest.TestCase):
    def test_parallel_edges_isolates_variants_and_same_source_resume(self):
        original = base()
        saved = copy.deepcopy(original)
        chunk1 = {"nodes": [{"id": "a", "label": "Alternate A", "evidence_quote": "line 9"}, {"id": "c", "label": "C"}],
                  "edges": [{"source": "a", "target": "c", "relation": "references", "source_file": "x.md", "source_location": "L9"}]}
        chunk2 = {"nodes": [{"id": "d", "label": "D"}],
                  "edges": [{"source": "a", "target": "c", "relation": "references", "source_file": "x.md", "source_location": "L10"},
                            {"source": "d", "target": "a", "relation": "references", "source_file": "x.md", "source_location": "L11"}]}
        g1 = union(original, [("chunk-1.json", "sha1", chunk1)])
        out = union(g1, [("chunk-2.json", "sha2", chunk2)])
        self.assertEqual(original, saved)
        self.assertEqual(out["nodes"][:len(saved["nodes"])], saved["nodes"])
        self.assertEqual(out["links"][:len(saved["links"])], saved["links"])
        self.assertEqual((len(out["nodes"]), len(out["links"])), (5, 5))
        self.assertIn({"id": "isolated", "label": "Isolated"}, out["nodes"])
        self.assertEqual(out["lossless_merge"]["node_variants"][0]["node"], chunk1["nodes"][0])
        self.assertEqual(union(out, [("chunk-1.json", "sha1", chunk1)]), out)
        with self.assertRaisesRegex(ValueError, "different SHA-256"):
            union(out, [("chunk-1.json", "changed", chunk1)])
        self.assertEqual(original, saved)

    def test_dangling_edges_and_duplicate_node_ids_rejected(self):
        with self.assertRaisesRegex(ValueError, "dangling"):
            union(base(), [("bad.json", "sha", {"edges": [{"source": "a", "target": "missing"}]})])
        bad = base()
        bad["nodes"].append({"id": "a"})
        with self.assertRaisesRegex(ValueError, "duplicate node"):
            validate_graph(bad)

    def test_mixed_keys_refused_before_networkx_can_overwrite(self):
        bad = base()
        bad["links"].append({"source": "a", "target": "b", "key": 0, "relation": "references"})
        with self.assertRaisesRegex(ValueError, "mixed keyed"):
            validate_graph(bad)

    def test_quarantine_keeps_exact_original_evidence_and_prevents_reentry(self):
        bad_edge = {"source": "a", "target": "b", "relation": "references", "source_file": "x.md", "evidence": [{"line": 8, "quote": "original quote"}]}
        chunk = {"edges": [bad_edge]}
        source = union(base(), [("chunk.json", "original-sha", chunk)])
        old = copy.deepcopy(source)
        fixed = dict(bad_edge, confidence="INFERRED", confidence_score=0.75)
        spec = [{"record_sha256": record_digest(bad_edge), "reason": "source does not support relation", "evidence": [{"source_file": "x.md", "line": 8}], "allowed_replacement_sha256": [record_digest(fixed)]}]
        out = quarantine_edges(source, spec)
        self.assertEqual(source, old)
        self.assertEqual(out["links"], base()["links"])
        self.assertEqual(out["lossless_merge"]["quarantined_edges"][0]["original_edge"], bad_edge)
        self.assertEqual(out["lossless_merge"]["quarantined_edges"][0]["evidence"], spec[0]["evidence"])
        # A previous input is an idempotent no-op; a new file cannot resurrect it.
        self.assertEqual(union(out, [("chunk.json", "original-sha", chunk)]), out)
        with self.assertRaisesRegex(ValueError, "reintroduce"):
            union(out, [("different-input.json", "new-sha", chunk)])
        with self.assertRaisesRegex(ValueError, "changed metadata"):
            union(out, [("mutated-input.json", "newer-sha", {"edges": [dict(bad_edge, owner="unverified")]})])
        # A different, explicitly corrected relationship is allowed.
        corrected = union(out, [("corrected.json", "corrected-sha", {"edges": [fixed]})])
        self.assertEqual(corrected["links"][-1], fixed)
        self.assertEqual(corrected["lossless_merge"]["quarantined_edges"][0]["original_edge"], bad_edge)

    def test_quarantine_refuses_structural_or_ambiguous_records(self):
        b = base()
        source = union(b, [])
        spec = [{"record_sha256": record_digest(b["links"][0]), "reason": "wrong", "evidence": ["x.md:L1"]}]
        with self.assertRaisesRegex(ValueError, "protected structural"):
            quarantine_edges(source, spec)
        edge = {"source": "a", "target": "b", "relation": "references", "evidence": "duplicate"}
        duplicated = union(b, [("a.json", "x", {"edges": [edge, edge]})])
        with self.assertRaisesRegex(ValueError, "exactly one"):
            quarantine_edges(duplicated, [{"record_sha256": record_digest(edge), "reason": "uncertain target", "evidence": ["x.md:L2"]}])
        mutated = dict(edge, owner="unverified")
        duplicated_identity = union(b, [("a.json", "x", {"edges": [edge, mutated]})])
        with self.assertRaisesRegex(ValueError, "duplicates quarantined identity"):
            quarantine_edges(duplicated_identity, [{"record_sha256": record_digest(edge), "reason": "wrong relationship", "evidence": ["x.md:L2"]}])

    def test_original_output_overwrite_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "base.json"
            p.write_text(json.dumps(base()))
            old = p.read_bytes()
            run = subprocess.run([sys.executable, str(Path(__file__).with_name("lossless_merge.py")),
                                  "--base", str(p), "--out", str(p)], capture_output=True)
            self.assertNotEqual(run.returncode, 0)
            self.assertEqual(p.read_bytes(), old)


if __name__ == "__main__":
    unittest.main()
