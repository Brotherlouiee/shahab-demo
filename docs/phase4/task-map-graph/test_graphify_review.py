"""Focused regressions for the Phase 4 Graphify review."""
import contextlib
import copy
import csv
import hashlib
import io
import json
import shutil
import sys
import subprocess
import tempfile
import time
import unittest
from collections import Counter, defaultdict
from pathlib import Path
from unittest.mock import patch

import replay_stage4 as replay
import build_task_map_graph as combined_graph

sys.path.insert(0, str(replay.ROOT / "docs/audits/phase2-source-coverage"))
import build_evidence_join_index as join
import build_and_validate as coverage_builder
import validate_phase4_snapshot as snapshot_validator


class CombinedGraphInputValidationTests(unittest.TestCase):
    def setUp(self):
        self.original_load_json = combined_graph.load_json
        self.sources = [
            self.original_load_json(combined_graph.ROOT / combined_graph.CODE_PATH),
            self.original_load_json(combined_graph.ROOT / combined_graph.TASK_PATH),
            self.original_load_json(combined_graph.ROOT / combined_graph.MAPPING_PATH),
        ]

    def assert_input_rejected(self, source_index, edit, message):
        sources = copy.deepcopy(self.sources)
        edit(sources[source_index])
        with patch.object(combined_graph, "load_json", side_effect=sources):
            with self.assertRaisesRegex(ValueError, message):
                combined_graph.build()

    def test_record_shape_and_identity_failures_are_controlled(self):
        cases = [
            (0, lambda data: data["nodes"].__setitem__(0, None), r"code.nodes\[0\] must be an object"),
            (0, lambda data: data["nodes"][0].pop("id"), r"code.nodes\[0\].id must be a non-empty string"),
            (0, lambda data: data["nodes"][0].update(id=None), r"code.nodes\[0\].id must be a non-empty string"),
            (0, lambda data: data["links"].__setitem__(0, None), r"code.links\[0\] must be an object"),
            (0, lambda data: data["links"][0].update(target="MISSING"), r"invalid edge endpoint"),
            (1, lambda data: data["nodes"][0].update(id=""), r"task.nodes\[0\].id must be a non-empty string"),
            (1, lambda data: next(node for node in data["nodes"] if node.get("node_type") == "TASK").update(parent_id="PACKAGE:MISSING"), r"invalid Package parent"),
            (1, lambda data: next(node for node in data["nodes"] if node.get("node_type") == "TASK").update(node_type="UNKNOWN"), r"node_type is invalid"),
            (1, lambda data: data["edges"][0].pop("source"), r"task.edges\[0\].source must be a non-empty string"),
            (2, lambda data: data["mappings"][0].pop("mapping_status"), r"mapping_status is invalid"),
            (2, lambda data: data["mappings"][0].update(mapping_status="UNKNOWN"), r"mapping_status is invalid"),
            (2, lambda data: data["mappings"][0].update(mapping_status=None), r"mapping_status is invalid"),
            (2, lambda data: data["mappings"][0].update(mapping_status=[]), r"mapping_status is invalid"),
            (2, lambda data: data["mappings"][0].update(current_code_node_refs=None), r"current_code_node_refs must be a list"),
            (2, lambda data: data["mappings"][0].update(package_ref=data["mappings"][1]["package_ref"]), r"duplicate mapping entity"),
            (2, lambda data: data["mappings"][0].update({
                key: None for key in ("entity_ref", "subtask_ref", "task_ref", "package_ref")
            }), r"lacks a non-empty entity reference"),
            (2, lambda data: data["open_decision_references"][0].update(mapping_status="MAPPED"), r"must remain BLOCKED"),
            (2, lambda data: data["open_decision_references"][0].update(mapping_status=[]), r"must remain BLOCKED"),
            (2, lambda data: data["open_decision_references"][0].update(decision_status="RESOLVED"), r"must remain OPEN"),
            (2, lambda data: data["open_decision_references"][0].update(task_refs=None), r"task_refs must be a list"),
            (2, lambda data: data["open_decision_references"][0].update(task_refs=["TASK:MISSING"]), r"decision scope endpoint missing"),
            (2, lambda data: data["open_decision_references"][0].update(open_decision_id=None), r"lacks a non-empty decision ID"),
        ]
        for source_index, edit, message in cases:
            with self.subTest(message=message):
                self.assert_input_rejected(source_index, edit, message)

    def test_unknown_non_contract_fields_remain_forward_compatible(self):
        sources = copy.deepcopy(self.sources)
        sources[2]["mappings"][0]["future_optional_metadata"] = {"label": "آزمایشی"}
        with patch.object(combined_graph, "load_json", side_effect=sources):
            graph = combined_graph.build()
        self.assertEqual(graph["counts"]["node_total"], 4490)


class CombinedGraphPublicationTests(unittest.TestCase):
    def output_pair(self, root):
        graph_path = root / "graph.json"
        html_path = root / "graph.html"
        graph_path.write_bytes(b"previous graph")
        html_path.write_bytes(b"previous viewer")
        return graph_path, html_path

    def assert_no_temporary_files(self, root, graph_path, html_path):
        self.assertEqual(set(root.iterdir()), {graph_path, html_path})

    def test_concurrent_processes_publish_one_coherent_generation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            graph_path, html_path = self.output_pair(root)
            marker = root / "first-publication-started"
            script = r'''import sys,time
from pathlib import Path
import build_task_map_graph as graph
mode,root,marker=sys.argv[1:]
original=graph.atomic_replace
def delayed(source,target):
    original(source,target)
    if mode=='A' and Path(target).name=='graph.json' and not Path(marker).exists():
        Path(marker).write_text('ready',encoding='utf-8')
        time.sleep(0.4)
graph.atomic_replace=delayed
root=Path(root);targets={'graph.json':root/'graph.json','viewer.html':root/'graph.html'}
order=['graph.json','viewer.html'] if mode=='A' else ['viewer.html','graph.json']
graph.publish_outputs([(targets[name],(mode+'-'+name).encode()) for name in order])
'''
            environment = dict(__import__("os").environ)
            module_directory = str(Path(combined_graph.__file__).resolve().parent)
            environment["PYTHONPATH"] = module_directory
            first = subprocess.Popen(
                [sys.executable, "-c", script, "A", str(root), str(marker)],
                cwd=combined_graph.ROOT,
                env=environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            try:
                deadline = time.monotonic() + 5
                while not marker.exists() and time.monotonic() < deadline:
                    time.sleep(0.01)
                self.assertTrue(marker.exists(), "first publisher did not reach the controlled interleaving")
                second = subprocess.Popen(
                    [sys.executable, "-c", script, "B", str(root), str(marker)],
                    cwd=combined_graph.ROOT,
                    env=environment,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                _, first_error = first.communicate(timeout=10)
                _, second_error = second.communicate(timeout=10)
                self.assertEqual(first.returncode, 0, first_error.decode(errors="replace"))
                self.assertEqual(second.returncode, 0, second_error.decode(errors="replace"))
                self.assertEqual(graph_path.read_bytes(), b"B-graph.json")
                self.assertEqual(html_path.read_bytes(), b"B-viewer.html")
            finally:
                if first.poll() is None:
                    first.kill()
                    first.wait(timeout=5)

    def test_html_replace_failure_restores_previous_json_and_html(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            graph_path, html_path = self.output_pair(root)
            original_replace = combined_graph.atomic_replace

            def fail_viewer_replace(source, target):
                if Path(target) == html_path:
                    raise OSError("injected viewer publication failure")
                return original_replace(source, target)

            with patch.object(combined_graph, "atomic_replace", side_effect=fail_viewer_replace):
                with self.assertRaisesRegex(OSError, "injected viewer publication failure"):
                    combined_graph.publish_outputs([
                        (graph_path, b"new graph"),
                        (html_path, b"new viewer"),
                    ])

            self.assertEqual(graph_path.read_bytes(), b"previous graph")
            self.assertEqual(html_path.read_bytes(), b"previous viewer")
            self.assert_no_temporary_files(root, graph_path, html_path)

    def test_failed_rollback_retains_recovery_backup(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            graph_path, html_path = self.output_pair(root)
            original_replace = combined_graph.atomic_replace
            def fail_publish_and_rollback(source, target):
                source, target = Path(source), Path(target)
                if target == html_path:
                    raise OSError("injected viewer publication failure")
                if target == graph_path and ".backup." in source.name:
                    raise OSError("injected graph rollback failure")
                return original_replace(source, target)
            with patch.object(combined_graph, "atomic_replace", side_effect=fail_publish_and_rollback):
                with self.assertRaisesRegex(OSError, "previous bytes retained at"):
                    combined_graph.publish_outputs([
                        (graph_path, b"new graph"), (html_path, b"new viewer")
                    ])
            self.assertEqual(graph_path.read_bytes(), b"new graph")
            self.assertEqual(html_path.read_bytes(), b"previous viewer")
            backups = list(root.glob(".graph.json.backup.*"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_bytes(), b"previous graph")
            self.assertEqual(len(list(root.glob(".graph.json.*"))), 1)
            self.assertEqual(len(list(root.glob(".graph.html.*"))), 0)

    def test_stage_fsync_failure_preserves_previous_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            graph_path, html_path = self.output_pair(root)
            with patch.object(combined_graph, "file_fsync", side_effect=OSError("injected fsync failure")):
                with self.assertRaisesRegex(OSError, "injected fsync failure"):
                    combined_graph.publish_outputs([
                        (graph_path, b"new graph"),
                        (html_path, b"new viewer"),
                    ])
            self.assertEqual(graph_path.read_bytes(), b"previous graph")
            self.assertEqual(html_path.read_bytes(), b"previous viewer")
            self.assert_no_temporary_files(root, graph_path, html_path)

    def test_directory_fsync_failure_restores_previous_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            graph_path, html_path = self.output_pair(root)
            with patch.object(combined_graph, "directory_fsync", side_effect=OSError("injected directory fsync failure")):
                with self.assertRaisesRegex(OSError, "injected directory fsync failure"):
                    combined_graph.publish_outputs([
                        (graph_path, b"new graph"),
                        (html_path, b"new viewer"),
                    ])
            self.assertEqual(graph_path.read_bytes(), b"previous graph")
            self.assertEqual(html_path.read_bytes(), b"previous viewer")
            self.assert_no_temporary_files(root, graph_path, html_path)

    def test_replace_failure_removes_new_file_when_no_previous_output_existed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            graph_path = root / "graph.json"
            html_path = root / "graph.html"
            original_replace = combined_graph.atomic_replace

            def fail_viewer_replace(source, target):
                if Path(target) == html_path:
                    raise OSError("injected viewer publication failure")
                return original_replace(source, target)

            with patch.object(combined_graph, "atomic_replace", side_effect=fail_viewer_replace):
                with self.assertRaisesRegex(OSError, "injected viewer publication failure"):
                    combined_graph.publish_outputs([
                        (graph_path, b"new graph"),
                        (html_path, b"new viewer"),
                    ])
            self.assertFalse(graph_path.exists())
            self.assertFalse(html_path.exists())
            self.assertEqual(list(root.iterdir()), [])

    def test_interrupt_during_second_replace_restores_previous_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            graph_path, html_path = self.output_pair(root)
            original_replace = combined_graph.atomic_replace

            def interrupt_viewer_replace(source, target):
                if Path(target) == html_path:
                    raise KeyboardInterrupt("injected interruption")
                return original_replace(source, target)

            with patch.object(combined_graph, "atomic_replace", side_effect=interrupt_viewer_replace):
                with self.assertRaisesRegex(KeyboardInterrupt, "injected interruption"):
                    combined_graph.publish_outputs([
                        (graph_path, b"new graph"),
                        (html_path, b"new viewer"),
                    ])
            self.assertEqual(graph_path.read_bytes(), b"previous graph")
            self.assertEqual(html_path.read_bytes(), b"previous viewer")
            self.assert_no_temporary_files(root, graph_path, html_path)


class CoverageBuilderTests(unittest.TestCase):
    def test_failed_machine_control_produces_failure_exit(self):
        validations = {
            "first": {"result": "PASS"},
            "second": {"result": "FAIL"},
        }
        self.assertTrue(coverage_builder.has_validation_failures([], validations))
        self.assertTrue(coverage_builder.has_validation_failures(["structural error"], {"first": {"result": "PASS"}}))
        self.assertFalse(coverage_builder.has_validation_failures([], {"first": {"result": "PASS"}}))

    def test_duplicate_csv_header_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.csv"
            path.write_text("id,id\nA,B\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate column.*id"):
                coverage_builder.read_csv(path)

    def test_unclosed_markdown_fence_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "unclosed.md"
            path.write_text("# Section\n\n```python\nprint('incomplete')\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, r"Unclosed fenced code block.*:3"):
                coverage_builder.parse_sources(path)

    def test_failed_atomic_csv_publication_preserves_previous_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "generated.csv"
            output.write_bytes(b"previous valid csv\n")
            with patch.object(coverage_builder, "atomic_replace", side_effect=OSError("injected replace failure")):
                with self.assertRaisesRegex(OSError, "injected replace failure"):
                    coverage_builder.write_csv(output, ["id", "value"], [{"id": "A", "value": "B"}])
            self.assertEqual(output.read_bytes(), b"previous valid csv\n")
            self.assertEqual(set(root.iterdir()), {output})

    def test_atomic_csv_stage_write_failure_preserves_previous_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "generated.csv"
            output.write_bytes(b"previous valid csv\n")
            with patch.object(coverage_builder, "file_fsync", side_effect=OSError("injected fsync failure")):
                with self.assertRaisesRegex(OSError, "injected fsync failure"):
                    coverage_builder.write_csv(output, ["id", "value"], [{"id": "A", "value": "B"}])
            self.assertEqual(output.read_bytes(), b"previous valid csv\n")
            self.assertEqual(set(root.iterdir()), {output})


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

    @contextlib.contextmanager
    def temporary_csv_edit(self, name, edit):
        path = self.coverage / name
        original = path.read_bytes()
        try:
            self.edit_csv(name, edit)
            yield
        finally:
            path.write_bytes(original)

    def assert_preserved_on_error(self, error):
        with self.assertRaisesRegex(ValueError, error):
            join.main()
        self.assertEqual(self.output.read_text(encoding="utf-8"), "previous valid index")

    def test_index_stage_fsync_failure_preserves_previous_output(self):
        with patch.object(join, "fsync", side_effect=OSError("injected fsync failure")):
            with self.assertRaisesRegex(OSError, "injected fsync failure"):
                join.publish_index(self.output, {"example": "new index"})
        self.assertEqual(self.output.read_text(encoding="utf-8"), "previous valid index")
        self.assertEqual(
            [path for path in self.coverage.iterdir() if path.name.startswith(".evidence-join-index.json.")],
            [],
        )

    def test_missing_required_headers_fail_before_publication(self):
        for name, columns in join.REQUIRED_COLUMNS.items():
            for column in sorted(columns):
                with (self.subTest(file=name, column=column),
                      self.temporary_csv_edit(name, lambda fields, rows: fields.remove(column))):
                    self.assert_preserved_on_error(rf"{name}: missing required columns: {column}")

    def test_canonical_headings_and_review_statuses(self):
        index = join.build()
        _, candidates = join.read_csv(self.coverage / "atomic-obligations.csv")
        _, inventory = join.read_csv(self.coverage / "source-inventory.csv")
        parents = {row["source_unit_id"]: row["hierarchy_or_title"] for row in inventory}
        expected = {row["candidate_id"]: parents[row["parent_heading_id"]] for row in candidates}
        self.assertTrue(expected)
        self.assertTrue(all(expected.values()))
        self.assertEqual({r["candidate_id"]: r["section_heading"] for r in index["candidate_index"]}, expected)
        self.assertEqual(index["totals"]["candidate_review_status_counts"],
                         dict(Counter(row["review_status"] for row in candidates)))
        nested = [atom for row in index["candidate_index"] for atom in row["atomic_obligations"]]
        self.assertEqual(len(nested), index["totals"]["atomic_obligations"])
        self.assertEqual(len({a["atomic_obligation_id"] for a in nested}), len(nested))
        self.assertEqual(dict(Counter(a["coverage_status"] for a in nested)),
                         index["totals"]["atomic_coverage_status_counts"])

    def test_legacy_heading_fallback(self):
        _, candidates = join.read_csv(self.coverage / "atomic-obligations.csv")
        candidate = candidates[0]

        def edit(fields, rows):
            fields.remove("hierarchy_or_title")
            fields.append("heading_text")
            parent = next(row for row in rows if row["source_unit_id"] == candidate["parent_heading_id"])
            parent["heading_text"] = "Legacy heading"

        self.edit_csv("source-inventory.csv", edit)
        items = join.build()["candidate_index"]
        self.assertEqual(items[0]["section_heading"], "Legacy heading")
        self.assertTrue(any(item["section_heading"] == "" for item in items))

    def test_trace_lists_drop_empty_references_consistently(self):
        fields_by_output = {
            "graph_node_ids": "graph_nodes",
            "owner_package_candidates": "packages",
            "requirement_candidates": "requirements",
            "task_subtask_candidates": "tasks",
            "ac_test_candidates": "ac_test",
        }
        def edit(fields, rows):
            rows[0].update(dict.fromkeys(fields_by_output, "; A ; ;B; "))

        self.edit_csv("execution-trace.csv", edit)
        _, trace = join.read_csv(self.coverage / "execution-trace.csv")
        item = next(row for row in join.build()["candidate_index"] if row["candidate_id"] == trace[0]["candidate_id"])
        for key in fields_by_output.values():
            with self.subTest(key=key):
                self.assertEqual(item[key], ["A", "B"])

    def test_duplicate_trace_and_review_ids_fail_before_publication(self):
        for name in ("execution-trace.csv", "semantic-review-dispositions.csv"):
            with (self.subTest(file=name),
                  self.temporary_csv_edit(name, lambda fields, rows: rows.append(rows[0]))):
                self.assert_preserved_on_error(rf"{name}: duplicate candidate_id")

    def test_short_csv_row_fails_before_publication(self):
        path = self.coverage / "atomic-obligations.csv"
        header = path.read_text(encoding="utf-8-sig").splitlines()[0]
        path.write_text(header + "\nID,\n", encoding="utf-8")
        self.assert_preserved_on_error(r"atomic-obligations.csv:2: missing value\(s\) in source_unit_id")

    def test_missing_pinned_graph_fails_before_publication(self):
        path = self.coverage / "missing-graph.json"
        with patch.object(join, "GRAPH_PATH", path), patch.object(join, "ROOT", self.coverage):
            self.assert_preserved_on_error(r"Pinned Graphify graph unavailable.*missing-graph.json")

    def test_graph_neighbors_only_include_unmapped_endpoints(self):
        graph = {
            "nodes": [{"id": name} for name in ("in-a", "in-b", "out-a", "out-b")],
            "links": [
                {"source": "in-a", "target": "in-b", "relation": "r", "confidence": "EXTRACTED", "weight": 10},
                {"source": "in-a", "target": "in-a", "relation": "r", "confidence": "EXTRACTED", "weight": 9},
                {"source": "out-a", "target": "in-a", "relation": "r", "confidence": "EXTRACTED", "weight": 2},
                {"source": "in-b", "target": "out-a", "relation": "r", "confidence": "EXTRACTED", "weight": 2},
                {"source": "in-b", "target": "out-b", "relation": "r", "confidence": "EXTRACTED", "weight": 1},
            ],
        }
        graph_path = self.coverage / "graph.json"
        graph_path.write_text(json.dumps(graph), encoding="utf-8")
        self.edit_csv("execution-trace.csv", lambda fields, rows: rows[0].update(graph_node_ids="in-a;in-b"))
        _, trace = join.read_csv(self.coverage / "execution-trace.csv")
        digest = hashlib.sha256(graph_path.read_bytes()).hexdigest()
        with patch.object(join, "GRAPH_PATH", graph_path), patch.object(join, "GRAPH_SHA256", digest):
            items = join.build()["candidate_index"]
        item = next(row for row in items if row["candidate_id"] == trace[0]["candidate_id"])
        self.assertEqual(item["graph_nodes"], ["in-a", "in-b"])
        self.assertEqual(item["graph_neighbors"], [
            {"node_id": name, "relation": "r", "confidence": "EXTRACTED"} for name in ("out-a", "out-b")
        ])

    def test_orphan_obligation_fails_before_publication(self):
        self.edit_csv("atomic-obligation-dispositions.csv",
                      lambda fields, rows: rows[0].update(candidate_id="UNKNOWN-CANDIDATE"))
        self.assert_preserved_on_error("references unknown candidate_id UNKNOWN-CANDIDATE")

    def test_duplicate_obligation_fails_before_publication(self):
        self.edit_csv("atomic-obligation-dispositions.csv", lambda fields, rows: rows.append(rows[0]))
        self.assert_preserved_on_error("duplicate atomic_obligation_id")

    def test_null_identifier_fails_with_controlled_error(self):
        self.edit_csv("atomic-obligations.csv", lambda fields, rows: rows[0].update(candidate_id=None))
        self.assert_preserved_on_error("atomic-obligations.csv: blank candidate_id")

    def test_failed_index_publication_preserves_previous_output(self):
        output = self.output.read_bytes()
        printed = io.StringIO()
        with (patch.object(join, "replace", side_effect=OSError("injected replace failure")),
              contextlib.redirect_stdout(printed),
              self.assertRaisesRegex(OSError, "injected replace failure")):
            join.main()
        self.assertEqual(self.output.read_bytes(), output)
        self.assertEqual(list(self.coverage.glob(".evidence-join-index.json.*")), [])
        self.assertNotIn("PASS", printed.getvalue())

    def test_duplicate_csv_headers_fail_before_publication(self):
        self.edit_csv("source-inventory.csv", lambda fields, rows: fields.append(fields[0]))
        self.assert_preserved_on_error("duplicate column")

    def test_pinned_graph_hash_mismatch_is_rejected(self):
        with patch.object(join, "GRAPH_SHA256", "0" * 64):
            with self.assertRaisesRegex(SystemExit, "Pinned Graphify graph SHA-256 mismatch"):
                join.build()
        self.assertEqual(self.output.read_text(encoding="utf-8"), "previous valid index")

    def test_pinned_graph_lookup_failure_is_controlled(self):
        missing_graph = join.ROOT / "docs/audits/phase2-source-coverage/.missing-pinned-graph.json"
        failure = subprocess.CalledProcessError(128, ["git", "show"])
        with patch.object(join, "GRAPH_PATH", missing_graph), patch.object(
            join.subprocess, "run", side_effect=failure
        ), self.assertRaisesRegex(ValueError, "Pinned Graphify graph unavailable"):
            join.build()
        self.assertEqual(self.output.read_text(encoding="utf-8"), "previous valid index")

    def test_join_main_publishes_valid_index(self):
        join.main()
        published = json.loads(self.output.read_text(encoding="utf-8"))
        self.assertEqual(published["totals"]["candidates"], 1633)
        self.assertEqual(published["totals"]["atomic_obligations"], 1285)

    def test_duplicate_candidate_fails_before_publication(self):
        self.edit_csv("atomic-obligations.csv", lambda fields, rows: rows.append(rows[0]))
        self.assert_preserved_on_error("duplicate candidate_id")


class CertifiedSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.email", "snapshot-test@example.invalid"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.name", "Snapshot Test"], cwd=self.root, check=True)
        subprocess.run(["git", "remote", "add", "origin", "https://github.com/Brotherlouiee/shahab-demo.git"], cwd=self.root, check=True)
        self.fixture_data = {path: ("fixture:" + path).encode() for path in snapshot_validator.REQUIRED_PATHS}
        code_path = "docs/phase4/task-map-graph/current-project-code-graph.json"
        task_path = "docs/phase4/task-map-graph/new-project-task-graph.json"
        mapping_path = "docs/phase4/task-map-graph/task-map-mapping.json"
        graph_path = "docs/phase4/task-map-graph/task-map-graph.json"
        ref_path = "knowledge-graph/phase2-reference-docs/semantic/graph.json"
        evidence_path = "docs/audits/phase2-source-coverage/evidence-join-index.json"
        code = {"nodes": []}
        task = {"nodes": ([{"node_type": "PACKAGE"}] * 36 + [{"node_type": "TASK"}] * 189 + [{"node_type": "SUBTASK"}] * 471)}
        mapping = {
            "mappings": ([{"mapping_status": "MAPPED"}] * 15 + [{"mapping_status": "PARTIALLY_MAPPED"}] * 27 + [{"mapping_status": "NEW_IMPLEMENTATION"}] * 654),
            "stage4_relation_overlay": {"relations": [{}] * 99},
            "open_decision_references": [{"decision_status": "OPEN", "mapping_status": "BLOCKED"}] * 134,
            "stage4_code_search_audit": {"records": [{}] * 657},
        }
        coverage = {"totals": {"candidates": 1633, "candidate_review_status_counts": {"SEMANTICALLY_REVIEWED": 1633},
                               "atomic_obligations": 1285,
                               "atomic_coverage_status_counts": {"VERIFIED_COVERED": 1149, "OPEN_DECISION": 134, "VERIFIED_UNCOVERED": 2}}}
        for path, obj in ((code_path, code), (task_path, task), (mapping_path, mapping),
                          (ref_path, {"nodes": []}), (evidence_path, coverage)):
            self.fixture_data[path] = json.dumps(obj, separators=(",", ":")).encode()
        graph = {
            "counts": {"node_total": 4490, "edge_total": 11435, "communities": 181},
            "source_inputs": {"current_project_code_graph": {"node_count": 3653},
                              "new_project_task_graph": {"node_count": 696}},
            "validation": {"result": "PASS", **{key: True for key in (
                "unique_node_ids", "all_edge_endpoints_valid", "all_task_graph_nodes_preserved",
                "all_code_graph_nodes_preserved", "all_source_edges_preserved", "lossless_source_snapshots_present",
                "open_decisions_preserved", "mapping_coverage", "immutable_graphs_unchanged",
                "all_source_data_references_valid", "lossless_source_payload_round_trip")}},
            "source_payloads": {name: {"data": __import__("base64").b64encode(__import__("gzip").compress(self.fixture_data[path], mtime=0)).decode(),
                                       "sha256_uncompressed": hashlib.sha256(self.fixture_data[path]).hexdigest()}
                                for name, path in (("current_project_code_graph", code_path),
                                                   ("new_project_task_graph", task_path), ("task_map_mapping", mapping_path))},
        }
        self.fixture_data[graph_path] = json.dumps(graph, separators=(",", ":")).encode()
        self.records = []
        for path in sorted(snapshot_validator.REQUIRED_PATHS):
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(self.fixture_data[path])
            blob = subprocess.check_output(["git", "hash-object", "-w", str(target)], cwd=self.root, text=True).strip()
            payload = target.read_bytes()
            self.records.append({"path": path, "sha256": hashlib.sha256(payload).hexdigest(),
                                 "size_bytes": len(payload), "git_blob_sha": blob,
                                 "role": "REQUIRED_PRIMARY_INPUT" if path in snapshot_validator.PRIMARY_PATHS else "REQUIRED_REFERENCE_INPUT",
                                 "required_for_phase5": True})
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "fixture snapshot"], cwd=self.root, check=True)
        self.commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.root, text=True).strip()
        self.pin_commit = patch.object(snapshot_validator, "APPROVED_SOURCE_COMMIT", self.commit)
        self.pin_commit.start()
        self.addCleanup(self.pin_commit.stop)
        self.pin_snapshot = patch.object(snapshot_validator, "APPROVED_SNAPSHOT_ID", "phase4-fixture")
        self.pin_snapshot.start()
        self.addCleanup(self.pin_snapshot.stop)
        self.pin_immutable = patch.object(snapshot_validator, "IMMUTABLE_SHA256", {
            path: hashlib.sha256(self.fixture_data[path]).hexdigest()
            for path in (code_path, task_path, ref_path)})
        self.pin_immutable.start()
        self.addCleanup(self.pin_immutable.stop)
        self.manifest_path = self.root / "manifest.json"
        self.write_manifest()
        self.commit_manifest()

    def commit_manifest(self):
        subprocess.run(["git", "add", "manifest.json"], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "fixture manifest"], cwd=self.root, check=True)

    def write_manifest(self, records=None, **overrides):
        values = list(self.records if records is None else records)
        primary = [r for r in values if r["role"] == "REQUIRED_PRIMARY_INPUT"]
        refs = [r for r in values if r["role"] != "REQUIRED_PRIMARY_INPUT"]
        manifest = {
            "manifest_schema_version": "1.0", "repository": snapshot_validator.REPOSITORY,
            "snapshot_id": "phase4-fixture", "certified_source_commit": self.commit,
            "source_pr": 257,
            "certification_status": "TECHNICALLY_VALID_FOR_PHASE5; FORMAL_PHASE4_ACCEPTANCE_CONDITIONAL",
            "formal_phase4_acceptance": "CONDITIONAL",
            "primary_inputs": primary, "reference_inputs": refs,
            "optional_human_review_artifacts": [], "audit_evidence_only": [],
            "graph_statistics": {"combined_graph_nodes": 4490, "combined_graph_edges": 11435,
                                  "communities": 181, "current_code_nodes": 3653, "task_graph_nodes": 696,
                                  "packages": 36, "tasks": 189, "subtasks": 471},
            "mapping_statistics": {"records": 696, "MAPPED": 15, "PARTIALLY_MAPPED": 27,
                                   "NEW_IMPLEMENTATION": 654, "relation_overlay": 99},
            "decision_statistics": {"open_decisions": 134, "blocked_mappings": 134,
                                     "stage4_replay_records": 657},
            "source_coverage_statistics": {"candidates": 1633, "pending_candidates": 0,
                                            "atomic_obligations": 1285, "covered": 1149,
                                            "partial": 0, "open_decision": 134, "uncovered": 2},
            "artifact_hashes": {r["path"]: r["sha256"] for r in values},
            "artifact_sizes": {r["path"]: r["size_bytes"] for r in values},
            "artifact_roles": {r["path"]: r["role"] for r in values},
        }
        manifest.update(overrides)
        self.manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        return manifest

    def test_01_certified_snapshot_is_accepted(self):
        result = snapshot_validator.validate(self.manifest_path, self.root)
        self.assertEqual(result["result"], "CERTIFIED_SNAPSHOT_VALID")

    def test_02_missing_required_artifact_is_rejected(self):
        path = self.records[0]["path"]
        (self.root / path).unlink()
        with self.assertRaisesRegex(snapshot_validator.SnapshotValidationError, path):
            snapshot_validator.validate(self.manifest_path, self.root)

    def test_03_changed_artifact_is_rejected(self):
        path = self.records[0]["path"]
        (self.root / path).write_bytes(b"tampered")
        with self.assertRaisesRegex(snapshot_validator.SnapshotValidationError, path):
            snapshot_validator.validate(self.manifest_path, self.root)

    def test_04_replaced_with_another_artifact_version_is_rejected(self):
        first, second = self.records[:2]
        (self.root / first["path"]).write_bytes((self.root / second["path"]).read_bytes())
        with self.assertRaisesRegex(snapshot_validator.SnapshotValidationError, first["path"]):
            snapshot_validator.validate(self.manifest_path, self.root)

    def test_05_incomplete_or_invalid_manifest_is_rejected(self):
        manifest = self.write_manifest()
        manifest.pop("reference_inputs")
        self.manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        self.commit_manifest()
        with self.assertRaisesRegex(snapshot_validator.SnapshotValidationError, "reference_inputs"):
            snapshot_validator.validate(self.manifest_path, self.root)
        duplicated = list(self.records) + [dict(self.records[0])]
        self.write_manifest(duplicated)
        self.commit_manifest()
        with self.assertRaisesRegex(snapshot_validator.SnapshotValidationError, "duplicate or ambiguous"):
            snapshot_validator.validate(self.manifest_path, self.root)

    def test_06_path_outside_repository_is_rejected(self):
        records = [dict(r) for r in self.records]
        records[0]["path"] = "../../outside.json"
        with self.assertRaisesRegex(snapshot_validator.SnapshotValidationError, "escapes repository"):
            snapshot_validator.validate(self.manifest_path, self.root) if False else self._validate_records(records)

    def _validate_records(self, records):
        self.write_manifest(records)
        self.commit_manifest()
        return snapshot_validator.validate(self.manifest_path, self.root)

    def test_07_changed_manifest_and_artifact_cannot_recertify_worktree(self):
        records = [dict(r) for r in self.records]
        item = records[0]
        changed = b"new generation"
        item.update(sha256=hashlib.sha256(changed).hexdigest(), size_bytes=len(changed), git_blob_sha="0" * 40)
        (self.root / item["path"]).write_bytes(changed)
        self.write_manifest(records)
        self.commit_manifest()
        with self.assertRaisesRegex(snapshot_validator.SnapshotValidationError, "certified commit"):
            snapshot_validator.validate(self.manifest_path, self.root)

    def test_manifest_header_contract_rejects_invalid_values(self):
        cases = [
            ("manifest_schema_version", "2.0", "manifest_schema_version"),
            ("repository", "someone/else", "repository does not match"),
            ("source_pr", 256, "source_pr is not the approved Phase 4 handoff PR"),
            ("certified_source_commit", "bad", "full Git SHA"),
            ("certified_source_commit", "0" * 40, "not the project-approved snapshot source"),
            ("snapshot_id", "phase4-other", "not the approved deterministic snapshot ID"),
            ("certification_status", "ACCEPTED", "not the approved technical-only status"),
            ("formal_phase4_acceptance", "ACCEPTED", "preserve conditional formal acceptance"),
        ]
        for key, value, message in cases:
            with self.subTest(key=key, value=value):
                self.write_manifest(**{key: value})
                self.commit_manifest()
                with self.assertRaisesRegex(snapshot_validator.SnapshotValidationError, message):
                    snapshot_validator.validate(self.manifest_path, self.root)

    def test_git_ancestry_command_os_error_is_controlled(self):
        original_run = snapshot_validator.subprocess.run
        def fail_ancestry(command, *args, **kwargs):
            if command[:3] == ["git", "merge-base", "--is-ancestor"]:
                raise OSError("injected git executable failure")
            return original_run(command, *args, **kwargs)
        with patch.object(snapshot_validator.subprocess, "run", side_effect=fail_ancestry):
            with self.assertRaisesRegex(snapshot_validator.SnapshotValidationError,
                                        "could not verify certified source commit ancestry"):
                snapshot_validator.validate(self.manifest_path, self.root)

    def test_boolean_artifact_size_is_not_an_integer(self):
        relative = "docs/optional-one-byte.bin"
        target = self.root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"x")
        subprocess.run(["git", "add", relative], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "one-byte optional artifact"], cwd=self.root, check=True)
        self.commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.root, text=True).strip()
        self.pin_commit.stop()
        replacement_pin = patch.object(snapshot_validator, "APPROVED_SOURCE_COMMIT", self.commit)
        replacement_pin.start()
        self.addCleanup(replacement_pin.stop)
        record = {"path": relative, "sha256": hashlib.sha256(b"x").hexdigest(),
                  "size_bytes": True, "git_blob_sha": subprocess.check_output(
                      ["git", "hash-object", "-w", str(target)], cwd=self.root, text=True).strip(),
                  "role": "OPTIONAL_HUMAN_REVIEW", "required_for_phase5": False}
        values = self.records + [record]
        references = [r for r in values if r["role"] == "REQUIRED_REFERENCE_INPUT"]
        self.write_manifest(records=values, reference_inputs=references,
                            optional_human_review_artifacts=[record])
        self.commit_manifest()
        with self.assertRaisesRegex(snapshot_validator.SnapshotValidationError, "invalid size_bytes"):
            snapshot_validator.validate(self.manifest_path, self.root)

    def test_non_object_artifact_record_returns_controlled_error(self):
        self.write_manifest(primary_inputs=[None])
        self.commit_manifest()
        with self.assertRaisesRegex(snapshot_validator.SnapshotValidationError,
                                    r"manifest.primary_inputs\[0\] must be an artifact object"):
            snapshot_validator.validate(self.manifest_path, self.root)

    def test_08_failure_returns_nonzero_and_never_changes_artifacts(self):
        before = {r["path"]: (self.root / r["path"]).read_bytes() for r in self.records}
        path = self.records[0]["path"]
        (self.root / path).write_bytes(b"invalid")
        before[path] = b"invalid"
        output, error = io.StringIO(), io.StringIO()
        with (patch.object(sys, "argv", ["validate_phase4_snapshot.py", "--manifest", str(self.manifest_path), "--repo-root", str(self.root)]),
              contextlib.redirect_stdout(output), contextlib.redirect_stderr(error)):
            self.assertEqual(snapshot_validator.main(), 1)
        self.assertEqual(output.getvalue(), "")
        self.assertIn("STOP_CONSUMPTION", error.getvalue())
        after = {r["path"]: (self.root / r["path"]).read_bytes() for r in self.records}
        self.assertEqual(after, before)


class ReplayTests(unittest.TestCase):
    def test_non_string_relation_endpoint_is_rejected_without_crashing(self):
        mapping = copy.deepcopy(replay.readj(replay.FILES["mapping"]))
        relation = mapping["stage4_relation_overlay"]["relations"][0]
        relation["source"] = None
        mapping["validation"]["semantic_replay_projection_sha256"] = replay.projection_digest(mapping)
        inputs = [mapping] + [
            replay.readj(replay.FILES[key])
            for key in ("task_graph", "current_code_graph", "reference_graph", "code_manifest")
        ]
        output = io.StringIO()
        with (patch.object(replay, "readj", side_effect=inputs),
              patch.object(sys, "argv", ["replay_stage4.py", "--check-only"]),
              contextlib.redirect_stdout(output)):
            self.assertEqual(replay.main(), 1)
        self.assertIn("relation endpoint is not a Package/Task/Contract/Decision ref", output.getvalue())
        self.assertIn("relation endpoint aliases disagree", output.getvalue())

    def test_replay_rejects_a_relation_overlay_hard_order_cycle(self):
        mapping = copy.deepcopy(replay.readj(replay.FILES["mapping"]))
        relation = next(
            item for item in mapping["stage4_relation_overlay"]["relations"]
            if item.get("relation_id") == "REL-STAGE4-036"
        )
        relation.update(
            source="TASK:CORE:C05B:001",
            target="TASK:CORE:C05B:002",
            source_node="TASK:CORE:C05B:001",
            target_node="TASK:CORE:C05B:002",
        )
        mapping["validation"]["semantic_replay_projection_sha256"] = replay.projection_digest(mapping)
        inputs = [mapping] + [
            replay.readj(replay.FILES[key])
            for key in ("task_graph", "current_code_graph", "reference_graph", "code_manifest")
        ]
        output = io.StringIO()
        with (
            patch.object(replay, "readj", side_effect=inputs),
            patch.object(sys, "argv", ["replay_stage4.py", "--check-only"]),
            contextlib.redirect_stdout(output),
        ):
            result = replay.main()
        self.assertEqual(result, 1)
        self.assertIn("HARD_ORDER cycle detected", output.getvalue())

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
                  patch.object(replay, "replace", side_effect=OSError("injected replace failure")),
                  contextlib.redirect_stdout(output),
                  self.assertRaisesRegex(OSError, "injected replace failure")):
                replay.main()
            self.assertEqual(target.read_bytes(), original)
            self.assertEqual(list(target.parent.iterdir()), [target])
            self.assertNotIn("PASS", output.getvalue())

    def test_mapping_stage_fsync_failure_preserves_previous_output_and_prints_no_pass(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "mapping.json"
            original = (replay.ROOT / replay.FILES["mapping"]).read_bytes()
            target.write_bytes(original)
            output = io.StringIO()
            with (
                patch.dict(replay.FILES, mapping=target),
                patch.object(sys, "argv", ["replay_stage4.py", "--write-code-search"]),
                patch.object(replay, "file_fsync", side_effect=OSError("injected fsync failure")),
                contextlib.redirect_stdout(output),
                self.assertRaisesRegex(OSError, "injected fsync failure"),
            ):
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
