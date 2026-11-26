"""Focused regressions for the Phase 4 Graphify review."""
import contextlib
import csv
import io
import json
import shutil
import sys
import tempfile
import unittest
from collections import defaultdict
from pathlib import Path
from unittest.mock import patch

import replay_stage4 as replay

sys.path.insert(0, str(replay.ROOT / "docs/audits/phase2-source-coverage"))
import build_evidence_join_index as join


class EvidenceJoinTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.coverage = Path(temporary.name)
        for name in join.REQUIRED_COLUMNS:
            shutil.copyfile(join.COVERAGE / name, self.coverage / name)
        self.output = self.coverage / "evidence-join-index.json"
        self.output.write_text("previous valid index", encoding="utf-8")
        patcher = patch.object(join, "COVERAGE", self.coverage)
        patcher.start()
        self.addCleanup(patcher.stop)

    def edit_csv(self, name, edit):
        path = self.coverage / name
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            fields, rows = list(reader.fieldnames), list(reader)
        edit(fields, rows)
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)

    def assert_preserved_on_error(self, error):
        with self.assertRaisesRegex(ValueError, error):
            join.main()
        self.assertEqual(self.output.read_text(encoding="utf-8"), "previous valid index")

    def test_missing_required_headers_fail_before_publication(self):
        for name, columns in join.REQUIRED_COLUMNS.items():
            with self.subTest(file=name):
                column = sorted(columns)[0]
                original = (self.coverage / name).read_bytes()
                self.edit_csv(name, lambda fields, rows: fields.remove(column))
                self.assert_preserved_on_error(rf"{name}: missing required columns: {column}")
                (self.coverage / name).write_bytes(original)

    def test_optional_heading_and_canonical_statuses(self):
        index = join.build()
        self.assertEqual(index["totals"]["candidate_review_status_counts"], {"SEMANTICALLY_REVIEWED": 1633})
        nested = [atom for row in index["candidate_index"] for atom in row["atomic_obligations"]]
        self.assertEqual(len(nested), index["totals"]["atomic_obligations"])
        self.assertEqual(len({a["atomic_obligation_id"] for a in nested}), len(nested))
        self.assertEqual(dict(replay.Counter(a["coverage_status"] for a in nested)),
                         index["totals"]["atomic_coverage_status_counts"])

    def test_orphan_obligation_fails_before_publication(self):
        self.edit_csv("atomic-obligation-dispositions.csv",
                      lambda fields, rows: rows[0].update(candidate_id="UNKNOWN-CANDIDATE"))
        self.assert_preserved_on_error("references unknown candidate_id UNKNOWN-CANDIDATE")

    def test_duplicate_obligation_fails_before_publication(self):
        self.edit_csv("atomic-obligation-dispositions.csv", lambda fields, rows: rows.append(rows[0]))
        self.assert_preserved_on_error("duplicate atomic_obligation_id")

    def test_duplicate_candidate_fails_before_publication(self):
        self.edit_csv("atomic-obligations.csv", lambda fields, rows: rows.append(rows[0]))
        self.assert_preserved_on_error("duplicate candidate_id")


class ReplayTests(unittest.TestCase):
    def test_exact_title_matching(self):
        real_path = "scripts/export_api_docs.py"
        cases = {
            "case": "ALPHA, bravo / CHARLIE",
            "spaces": "Alpha\n Bravo\t  Charlie",
            "multilingual": "قرارداد AlphaK / Bravo؛ Charlie بعدی",
            "substring": "alpha elsewhere charlie; prefixalpha bravo charliepost",
            "missing": "Alpha Bravo",
            real_path: (replay.ROOT / real_path).read_text(encoding="utf-8"),
        }
        corpus = [{"path": path, "blob_sha": "test", "text": text} for path, text in cases.items()]
        files = defaultdict(set)
        for i, source in enumerate(corpus):
            for token in replay.title_search_tokens(source["text"]):
                files[token].add(i)
        match_paths = lambda title: [row["file"] for row in replay.exact_title_matches(title, corpus, files)]
        self.assertEqual(match_paths("Alpha Bravo Charlie"), ["case", "spaces", "multilingual"])
        self.assertEqual(match_paths("قرارداد OpenAPI/Schema و version قبل از پیاده‌سازی"), [real_path])
        self.assertEqual(match_paths("Alpha Bravo"), [])

    def test_partial_evidence_by_id_and_validation(self):
        partial = {"task": ("code-b", "code-a")}
        evidence = {"code-a": ("a.py", 1), "code-b": ("b.py", 1)}
        nodes = {"code-a": {"source_file": "a.py"}, "code-b": {"source_file": "b.py"}}
        corpus = {"a.py": {"lines": ["def a(): pass"]}, "b.py": {"lines": ["def b(): pass"]}}
        replay.validate_partial_files(partial, evidence, nodes, corpus)
        variants = [
            ({"code-a": evidence["code-a"]}, nodes, corpus, "missing.*code-b"),
            (dict(evidence, extra=("a.py", 1)), nodes, corpus, "unexpected.*extra"),
            (evidence, {"code-a": nodes["code-a"]}, corpus, "code ID/file mismatch"),
            (evidence, nodes, {"a.py": corpus["a.py"]}, "evidence not found"),
            (dict(evidence, **{"code-b": ("b.py", 2)}), nodes, corpus, "evidence not found"),
        ]
        for files, code_nodes, sources, error in variants:
            with self.subTest(error=error), self.assertRaisesRegex(ValueError, error):
                replay.validate_partial_files(partial, files, code_nodes, sources)

    def test_partials_keep_pinned_code_locators(self):
        mapping = replay.readj(replay.FILES["mapping"])
        records = mapping["stage4_code_search_audit"]["records"]
        for record in records:
            ref = record["task_or_package_ref"]
            if ref in replay.PARTIAL:
                actual = {h["code_node_ref"]: (h["file"], h["line"]) for h in record["code_search_hits"]}
                self.assertEqual(actual, {code_id: replay.PARTIAL_FILES[code_id] for code_id in replay.PARTIAL[ref]})

    def test_failed_atomic_publication_preserves_mapping_and_prints_no_pass(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "mapping.json"
            original = (replay.ROOT / replay.FILES["mapping"]).read_bytes()
            target.write_bytes(original)
            output = io.StringIO()
            with (patch.dict(replay.FILES, mapping=target),
                  patch.object(sys, "argv", ["replay_stage4.py", "--write-code-search"]),
                  patch.object(replay.os, "replace", side_effect=OSError("injected replace failure")),
                  contextlib.redirect_stdout(output),
                  self.assertRaisesRegex(OSError, "injected replace failure")):
                replay.main()
            self.assertEqual(target.read_bytes(), original)
            self.assertEqual(list(target.parent.iterdir()), [target])
            self.assertNotIn("PASS", output.getvalue())

    def test_invalid_mapping_is_not_published(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "mapping.json"
            mapping = replay.readj(replay.FILES["mapping"])
            mapping["open_decision_references"][0]["mapping_status"] = "MAPPED"
            original = json.dumps(mapping).encode()
            target.write_bytes(original)
            output = io.StringIO()
            with (patch.dict(replay.FILES, mapping=target),
                  patch.object(sys, "argv", ["replay_stage4.py", "--write-code-search"]),
                  contextlib.redirect_stdout(output)):
                self.assertEqual(replay.main(), 1)
            self.assertIn("FAIL", output.getvalue())
            self.assertNotIn("PASS", output.getvalue())
            self.assertEqual(target.read_bytes(), original)


if __name__ == "__main__":
    unittest.main(verbosity=2)
