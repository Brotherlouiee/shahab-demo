"""Focused regressions for the Phase 4 Graphify review."""
import contextlib
import copy
import csv
import hashlib
import io
import json
import re
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

    def test_additional_input_contract_failures_fail_closed(self):
        cases = [
            (0, lambda data: data.update(nodes=None), r"code.nodes must be a list"),
            (0, lambda data: data["nodes"].__setitem__(0, 7), r"code.nodes\[0\] must be an object"),
            (1, lambda data: data["nodes"].__setitem__(0, None), r"task.nodes\[0\] must be an object"),
            (1, lambda data: next(node for node in data["nodes"] if node.get("node_type") == "SUBTASK").update(parent_id="PACKAGE:MISSING"), r"invalid Task parent"),
            (1, lambda data: next(node for node in data["nodes"] if node.get("node_type") == "TASK").update(parent_id=""), r"parent_id must be a non-empty string"),
            (0, lambda data: data["nodes"][1].update(id=data["nodes"][0]["id"]), r"duplicate code-node ids"),
            (1, lambda data: data["nodes"][1].update(id=data["nodes"][0]["id"]), r"duplicate task-graph node ids"),
            (2, lambda data: data.update(mappings=None), r"mapping.mappings must be a list"),
            (2, lambda data: data["mappings"].__setitem__(0, None), r"mapping.mappings\[0\] must be an object"),
            (2, lambda data: data["mappings"][0].update(source_graph_refs=[""]), r"source_graph_refs must be a list of non-empty strings"),
            (2, lambda data: data["open_decision_references"][0].update(decision_status="CLOSED"), r"must remain OPEN"),
            (2, lambda data: data["open_decision_references"][0].update(package_refs=[], task_refs=[]), r"has no Package or Task scope"),
            (2, lambda data: data["open_decision_references"][1].update(open_decision_id=data["open_decision_references"][0]["open_decision_id"]), r"duplicate open decision id"),
        ]
        for source_index, edit, message in cases:
            with self.subTest(message=message):
                sources = copy.deepcopy(self.sources)
                edit(sources[source_index])
                with patch.object(combined_graph, "load_json", side_effect=sources):
                    with self.assertRaisesRegex(ValueError, message):
                        combined_graph.build()

    def test_immutable_input_drift_is_rejected_before_graph_publication(self):
        expected = copy.deepcopy(combined_graph.EXPECTED_IMMUTABLE)
        first = next(iter(expected))
        expected[first]["sha256"] = "0" * 64
        with patch.object(combined_graph, "EXPECTED_IMMUTABLE", expected):
            with self.assertRaisesRegex(ValueError, "immutable input changed"):
                combined_graph.build()

    def test_mapping_to_unknown_code_node_is_rejected(self):
        sources = copy.deepcopy(self.sources)
        sources[2]["mappings"][0]["current_code_node_refs"].append("CODE:DOES_NOT_EXIST")
        with patch.object(combined_graph, "load_json", side_effect=sources):
            with self.assertRaisesRegex(ValueError, "references missing current-code node"):
                combined_graph.build()

    def test_optional_community_and_external_decision_reference_are_preserved(self):
        sources = copy.deepcopy(self.sources)
        sources[0]["nodes"][0]["community"] = None
        package_id = next(node["id"] for node in sources[1]["nodes"] if node["node_type"] == "PACKAGE")
        sources[2]["stage4_relation_overlay"]["relations"].append({
            "relation_id": "TEST:EXTERNAL-DECISION-REF",
            "source_node": package_id,
            "target_node": "DECISION:EXTERNAL-REF",
            "target_kind": "DECISION",
            "relation_type": "references",
            "rationale": "controlled coverage fixture",
        })
        with patch.object(combined_graph, "load_json", side_effect=sources):
            graph = combined_graph.build()
        external = next(node for node in graph["nodes"] if node["id"] == "DECISION:EXTERNAL-REF")
        self.assertEqual(external["node_type"], "DECISION_REFERENCE")
        self.assertEqual(external["declared_target_kind"], "DECISION")
        community_members = {member for community in graph["communities"] for member in community["member_node_ids"]}
        self.assertNotIn("CODE:" + str(sources[0]["nodes"][0]["id"]), community_members)

    def test_external_contract_reference_without_declared_kind_is_preserved(self):
        sources = copy.deepcopy(self.sources)
        package_id = next(node["id"] for node in sources[1]["nodes"] if node["node_type"] == "PACKAGE")
        sources[2]["stage4_relation_overlay"]["relations"].append({
            "relation_id": "TEST:CONTRACT-WITHOUT-KIND",
            "source_node": package_id,
            "target_node": "CONTRACT:OPTIONAL-KIND",
            "relation_type": "requires_contract",
        })
        with patch.object(combined_graph, "load_json", side_effect=sources):
            graph = combined_graph.build()
        node = next(item for item in graph["nodes"] if item["id"] == "CONTRACT:OPTIONAL-KIND")
        self.assertEqual(node["node_type"], "CONTRACT_REFERENCE")
        self.assertIsNone(node["declared_target_kind"])

    def test_reference_key_precedence_with_parallel_task_refs(self):
        sources = copy.deepcopy(self.sources)
        first, second = sources[2]["mappings"][:2]
        first_id, second_id = first["package_ref"], second["package_ref"]
        for row, package_id in ((first, first_id), (second, second_id)):
            row.pop("package_ref")
            row["task_ref"] = "TASK:SHARED-PARENT"
            row["subtask_ref"] = package_id
        with patch.object(combined_graph, "load_json", side_effect=sources):
            graph = combined_graph.build()
        self.assertEqual(graph["counts"]["node_total"], 4490)

    def test_explicit_entity_refs_make_duplicate_precheck_false(self):
        sources = copy.deepcopy(self.sources)
        for row in sources[2]["mappings"]:
            canonical = row.get("entity_ref") or row.get("subtask_ref") or row.get("task_ref") or row.get("package_ref")
            row["entity_ref"] = canonical
        with patch.object(combined_graph, "load_json", side_effect=sources):
            graph = combined_graph.build()
        self.assertEqual(graph["counts"]["node_total"], 4490)

    def test_noncanonical_decision_count_is_rejected(self):
        sources = copy.deepcopy(self.sources)
        sources[2]["open_decision_references"].pop()
        with patch.object(combined_graph, "load_json", side_effect=sources):
            with self.assertRaisesRegex(ValueError, "expected 134 open decisions"):
                combined_graph.build()

    def test_namespace_collision_is_rejected_after_unification(self):
        sources = copy.deepcopy(self.sources)
        code_id = str(sources[0]["nodes"][0]["id"])
        colliding_id = "CODE:" + code_id
        sources[1]["nodes"].append({"id": colliding_id, "node_type": "PACKAGE", "label": "collision fixture"})
        sources[2]["mappings"].append({
            "entity_ref": colliding_id,
            "mapping_status": "NEW_IMPLEMENTATION",
            "current_code_node_refs": [],
            "source_graph_refs": [],
        })
        with patch.object(combined_graph, "load_json", side_effect=sources):
            with self.assertRaisesRegex(ValueError, "duplicate unified node ids"):
                combined_graph.build()

    def test_unknown_external_overlay_reference_is_rejected(self):
        sources = copy.deepcopy(self.sources)
        package_id = next(node["id"] for node in sources[1]["nodes"] if node["node_type"] == "PACKAGE")
        sources[2]["stage4_relation_overlay"]["relations"].append({
            "relation_id": "TEST:UNKNOWN-REF",
            "source_node": package_id,
            "target_node": "EXTERNAL:UNKNOWN",
            "target_kind": "",
            "relation_type": "references",
        })
        with patch.object(combined_graph, "load_json", side_effect=sources):
            with self.assertRaisesRegex(ValueError, "invalid edge endpoint"):
                combined_graph.build()


class CombinedGraphCliTests(unittest.TestCase):
    def test_cli_check_only_and_atomic_output_modes(self):
        root = combined_graph.ROOT
        with tempfile.TemporaryDirectory(dir=root) as directory:
            out_dir = Path(directory)
            relative_output = out_dir.relative_to(root) / "graph.json"
            with patch.object(sys, "argv", ["build_task_map_graph.py", "--check-only", "--output", str(relative_output)]):
                self.assertEqual(combined_graph.main(), 0)
            output = out_dir / "graph.json"
            viewer = relative_output.with_name("viewer.html")
            with patch.object(sys, "argv", ["build_task_map_graph.py", "--output", str(output), "--html-output", str(viewer)]):
                self.assertEqual(combined_graph.main(), 0)
            graph = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(graph["counts"]["node_total"], 4490)
            self.assertEqual(graph["counts"]["edge_total"], 11435)
            self.assertIn('window.taskMapGraphReady', (root / viewer).read_text(encoding="utf-8"))
            no_html = out_dir / "graph-no-html.json"
            with patch.object(sys, "argv", ["build_task_map_graph.py", "--output", str(no_html), "--no-html"]):
                self.assertEqual(combined_graph.main(), 0)
            self.assertTrue(no_html.is_file())
            absolute_viewer = out_dir / "absolute-viewer.html"
            absolute_graph = out_dir / "absolute-viewer-graph.json"
            with patch.object(sys, "argv", ["build_task_map_graph.py", "--output", str(absolute_graph), "--html-output", str(absolute_viewer)]):
                self.assertEqual(combined_graph.main(), 0)
            self.assertIn('window.taskMapGraphReady', absolute_viewer.read_text(encoding="utf-8"))

    def test_script_entrypoint_runs_check_only(self):
        source = Path(combined_graph.__file__).read_text(encoding="utf-8")
        namespace = {"__name__": "__main__", "__file__": combined_graph.__file__}
        output = io.StringIO()
        with (patch.object(sys, "argv", ["build_task_map_graph.py", "--check-only"]),
              contextlib.redirect_stdout(output), self.assertRaises(SystemExit) as exit_result):
            exec(compile(source, combined_graph.__file__, "exec"), namespace)
        self.assertEqual(exit_result.exception.code, 0)
        self.assertIn('"result": "PASS"', output.getvalue())


class CombinedGraphPublicationTests(unittest.TestCase):
    def output_pair(self, root):
        graph_path = root / "graph.json"
        html_path = root / "graph.html"
        graph_path.write_bytes(b"previous graph")
        html_path.write_bytes(b"previous viewer")
        return graph_path, html_path

    def assert_no_temporary_files(self, root, graph_path, html_path):
        self.assertEqual(set(root.iterdir()), {graph_path, html_path})

    def test_empty_publication_is_a_noop(self):
        combined_graph.publish_outputs([])

    def test_existing_lock_file_does_not_append_a_lock_byte(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "out.json"
            target_key = "\0".join([str(target.resolve())])
            lock_name = hashlib.sha256(target_key.encode("utf-8")).hexdigest()
            lock_path = Path(tempfile.gettempdir()) / f"shahab-graph-publication-{lock_name}.lock"
            lock_path.write_bytes(b"existing-lock-byte")
            calls = []
            windows_os = type("WindowsOS", (), {"name": "nt", "SEEK_END": 2})()
            msvcrt = type("Msvcrt", (), {
                "LK_LOCK": 1, "LK_UNLCK": 2,
                "locking": staticmethod(lambda descriptor, mode, count: calls.append((mode, count))),
            })
            try:
                with patch.object(combined_graph, "os", windows_os), patch.dict(sys.modules, {"msvcrt": msvcrt}):
                    with combined_graph.publication_lock([(target, b"payload")]):
                        self.assertEqual(lock_path.read_bytes(), b"existing-lock-byte")
            finally:
                lock_path.unlink(missing_ok=True)
            self.assertEqual(calls, [(msvcrt.LK_LOCK, 1), (msvcrt.LK_UNLCK, 1)])

    def test_publication_without_directory_fsync_platform_capability(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "out.json"
            original_os = combined_graph.os
            proxy = type("PosixWithoutDirectoryFsync", (), {
                "name": "posix", "O_RDONLY": original_os.O_RDONLY,
                "chmod": staticmethod(original_os.chmod),
                "open": staticmethod(original_os.open),
                "close": staticmethod(original_os.close),
            })()
            with patch.object(combined_graph, "os", proxy):
                combined_graph.publish_outputs([(target, b"published")])
            self.assertEqual(target.read_bytes(), b"published")

    def test_rollback_unlink_failure_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            graph_path = root / "graph.json"
            html_path = root / "graph.html"
            original_replace = combined_graph.atomic_replace
            original_unlink = Path.unlink

            def fail_viewer_replace(source, target):
                if Path(target) == html_path:
                    raise OSError("injected viewer failure")
                return original_replace(source, target)

            def fail_graph_unlink(path, *args, **kwargs):
                if path == graph_path:
                    raise OSError("injected rollback unlink failure")
                return original_unlink(path, *args, **kwargs)

            with patch.object(combined_graph, "atomic_replace", side_effect=fail_viewer_replace), patch.object(Path, "unlink", fail_graph_unlink):
                with self.assertRaisesRegex(OSError, "rollback also failed.*injected rollback unlink failure"):
                    combined_graph.publish_outputs([(graph_path, b"new graph"), (html_path, b"new html")])
            self.assertEqual(graph_path.read_bytes(), b"new graph")

    def test_windows_lock_path_is_exercised_with_scoped_platform_stub(self):
        calls = []
        windows_os = type("WindowsOS", (), {"name": "nt", "SEEK_END": 2})()
        msvcrt = type("Msvcrt", (), {
            "LK_LOCK": 1,
            "LK_UNLCK": 2,
            "locking": staticmethod(lambda descriptor, mode, count: calls.append((mode, count))),
        })
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "out.json"
            with patch.object(combined_graph, "os", windows_os), patch.dict(sys.modules, {"msvcrt": msvcrt}):
                with combined_graph.publication_lock([(target, b"payload")]):
                    self.assertTrue(target.parent.exists())
        self.assertEqual(calls, [(msvcrt.LK_LOCK, 1), (msvcrt.LK_UNLCK, 1)])

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
    @staticmethod
    def write_ledger(path, fields, rows):
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)

    def test_apply_review_dispositions_missing_invalid_and_valid_ledgers(self):
        candidate = {
            "candidate_id": "CAND-1",
            "document": "docs/example.md",
            "start_line": 4,
            "source_unit_id": "UNIT-1",
        }
        fields = [
            "candidate_id", "semantic_disposition", "normative_status",
            "coverage_status", "atomicity_status", "source_evidence",
            "review_rationale", "reviewer", "review_date",
            "atomic_obligation_id", "normalized_obligation", "related_packages",
            "plan_evidence",
        ]
        row = {
            "candidate_id": "CAND-1",
            "semantic_disposition": "VERIFIED_COVERED",
            "normative_status": "NORMATIVE_APPROVED",
            "coverage_status": "VERIFIED_COVERED",
            "atomicity_status": "ATOMIC",
            "source_evidence": "docs/example.md:4 (UNIT-1); exact source",
            "review_rationale": "Direct evidence",
            "reviewer": "Reviewer",
            "review_date": "2026-11-27",
            "atomic_obligation_id": "ATOM-1",
            "normalized_obligation": "Example obligation",
            "related_packages": "C01",
            "plan_evidence": "plan:L22",
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ledger = root / "semantic-review-dispositions.csv"
            with patch.object(coverage_builder, "COVERAGE", root):
                coverage_builder.apply_review_dispositions([candidate.copy()])

                self.write_ledger(ledger, fields[1:], [row])
                with self.assertRaisesRegex(ValueError, "missing columns"):
                    coverage_builder.apply_review_dispositions([candidate.copy()])

                self.write_ledger(ledger, fields, [row, row])
                with self.assertRaisesRegex(ValueError, "Duplicate semantic review"):
                    coverage_builder.apply_review_dispositions([candidate.copy()])

                self.write_ledger(ledger, fields, [{**row, "candidate_id": "UNKNOWN"}])
                with self.assertRaisesRegex(ValueError, "unknown candidate"):
                    coverage_builder.apply_review_dispositions([candidate.copy()])

                self.write_ledger(ledger, fields, [{**row, "reviewer": ""}])
                with self.assertRaisesRegex(ValueError, "missing evidence or rationale"):
                    coverage_builder.apply_review_dispositions([candidate.copy()])

                self.write_ledger(ledger, fields, [{**row, "source_evidence": "docs/example.md:5 (UNIT-1)"}])
                with self.assertRaisesRegex(ValueError, "locator drift"):
                    coverage_builder.apply_review_dispositions([candidate.copy()])

                self.write_ledger(ledger, fields, [row])
                reviewed = candidate.copy()
                coverage_builder.apply_review_dispositions([reviewed])
                self.assertEqual(reviewed["review_status"], "SEMANTICALLY_REVIEWED")
                self.assertEqual(reviewed["classification_method"], "HUMAN_SEMANTIC_REVIEW")
                self.assertEqual(reviewed["atomic_obligation_id"], "ATOM-1")
                self.assertEqual(reviewed["logical_owner"], "C01")

    def test_apply_source_unit_dispositions_rejects_bad_rows_and_applies_valid_row(self):
        inventory_row = {
            "source_unit_id": "UNIT-HEADING",
            "document": "docs/example.md",
            "start_line": 2,
            "end_line": 2,
            "unit_type": "HEADING",
        }
        fields = [
            "source_unit_id", "unit_type", "semantic_disposition", "normative_status",
            "coverage_status", "source_evidence", "review_rationale", "reviewer", "review_date",
        ]
        row = {
            "source_unit_id": "UNIT-HEADING", "unit_type": "HEADING",
            "semantic_disposition": "STRUCTURAL_SECTION_LOCATOR",
            "normative_status": "NOT_APPLICABLE", "coverage_status": "NOT_APPLICABLE",
            "source_evidence": "docs/example.md:2-2 (UNIT-HEADING)",
            "review_rationale": "Heading only", "reviewer": "Reviewer", "review_date": "2026-11-27",
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ledger = root / "source-unit-review-dispositions.csv"
            with patch.object(coverage_builder, "COVERAGE", root):
                coverage_builder.apply_source_unit_dispositions([inventory_row.copy()])
                self.write_ledger(ledger, fields[1:], [row])
                with self.assertRaisesRegex(ValueError, "missing columns"):
                    coverage_builder.apply_source_unit_dispositions([inventory_row.copy()])
                self.write_ledger(ledger, fields, [{**row, "unit_type": "TEXT"}])
                with self.assertRaisesRegex(ValueError, "Invalid source-unit disposition"):
                    coverage_builder.apply_source_unit_dispositions([inventory_row.copy()])
                self.write_ledger(ledger, fields, [row, row])
                with self.assertRaisesRegex(ValueError, "Duplicate or unknown source unit"):
                    coverage_builder.apply_source_unit_dispositions([inventory_row.copy()])
                self.write_ledger(ledger, fields, [{**row, "source_evidence": "wrong locator"}])
                with self.assertRaisesRegex(ValueError, "Invalid source-unit disposition"):
                    coverage_builder.apply_source_unit_dispositions([inventory_row.copy()])
                valid = inventory_row.copy()
                self.write_ledger(ledger, fields, [row])
                coverage_builder.apply_source_unit_dispositions([valid])
                self.assertEqual(valid["coverage_status"], "NOT_APPLICABLE")
                self.assertEqual(valid["review_reason"], "Heading only")

    def test_pure_markdown_helpers_cover_empty_and_boundary_inputs(self):
        self.assertEqual(coverage_builder.line_bounds("unknown"), None)
        self.assertEqual(coverage_builder.line_bounds("L8–L12"), (8, 12))
        self.assertEqual(coverage_builder.line_bounds("line 19"), (19, 19))
        self.assertEqual(coverage_builder.cells_from_row("| A | B |"), ["A", "B"])
        self.assertEqual(coverage_builder.cells_from_row(r"A\|B|C"), ["A|B", "C"])
        self.assertEqual(coverage_builder.excerpt_text("first  \nsecond\t\n"), "first\nsecond")
        with tempfile.TemporaryDirectory() as directory:
            empty = Path(directory) / "empty.md"
            empty.write_text("", encoding="utf-8")
            parsed = coverage_builder.parse_sources(empty)
            self.assertEqual(parsed["headings"], [])
            self.assertEqual(parsed["tables"], [])
            self.assertEqual(parsed["paragraphs"], [])

    def test_classification_rule_precedence_and_all_terminal_states(self):
        self.assertEqual(coverage_builder.classification("must", is_heading=True)[0], "NEEDS_REVIEW")
        self.assertEqual(coverage_builder.classification("must", is_table_header=True)[0], "DESCRIPTIVE")
        self.assertEqual(coverage_builder.classification("obsolete",)[0], "SUPERSEDED")
        self.assertEqual(coverage_builder.classification("obsolete and must")[0], "MIXED")
        self.assertEqual(coverage_builder.classification("example and must")[0], "MIXED")
        self.assertEqual(coverage_builder.classification("open decision")[0], "NORMATIVE_OPEN_DECISION")
        self.assertEqual(coverage_builder.classification("example scenario")[0], "EXAMPLE")
        self.assertEqual(coverage_builder.classification("out of scope")[0], "OUT_OF_SCOPE")
        self.assertEqual(coverage_builder.classification("must be retained")[0], "NORMATIVE_APPROVED")
        self.assertEqual(coverage_builder.classification("Version 2 reference")[0], "DESCRIPTIVE")
        self.assertEqual(coverage_builder.classification("neutral description")[0], "NEEDS_REVIEW")

    def test_markdown_parser_handles_nested_headings_mixed_fences_and_tables(self):
        source = (
            "intro text\n"
            "### Child\n"
            "body before table\n"
            "| H1 | H2 |\n"
            "| --- | --- |\n"
            "| X | Y |\n"
            "\n"
            "````python\n"
            "print('one')\n"
            "```\n"
            "still inside\n"
            "````\n"
            "~~~js\n"
            "console.log('two')\n"
            "~~~\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested.md"
            path.write_text(source, encoding="utf-8")
            parsed = coverage_builder.parse_sources(path)
        self.assertEqual([h["title"] for h in parsed["headings"]], ["Child"])
        self.assertEqual(parsed["headings"][0]["path"], "Child")
        self.assertEqual(len(parsed["tables"]), 1)
        self.assertEqual(parsed["tables"][0]["rows"], [4, 6])
        self.assertEqual(len(parsed["code_blocks"]), 2)
        self.assertIn("still inside", parsed["code_blocks"][0]["text"])

    def test_graph_data_uses_only_hash_pinned_local_fallback(self):
        original = coverage_builder.subprocess.check_output
        with patch.object(coverage_builder.subprocess, "check_output", side_effect=subprocess.CalledProcessError(128, ["git", "show"])):
            nodes, digest = coverage_builder.graph_data()
        self.assertTrue(nodes)
        self.assertEqual(digest, "f16e684dc773e9bf053e51da2a0a37e3b5ffaf88809e1b5d37f8befbf69e1c93")
        with tempfile.TemporaryDirectory() as directory, patch.object(coverage_builder, "ROOT", Path(directory)):
            with patch.object(coverage_builder.subprocess, "check_output", side_effect=subprocess.CalledProcessError(128, ["git", "show"])):
                with self.assertRaisesRegex(RuntimeError, "Cannot read pinned Graphify graph"):
                    coverage_builder.graph_data()

    def test_package_index_keeps_unheaded_package_and_pending_candidate_gap(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan = root / "plan.md"
            plan.write_text("| C01 | Package | PASS | PASS | PLANNING_ACCEPTED |\n", encoding="utf-8")
            (root / "atomic-obligation-dispositions.csv").write_text(
                "atomic_obligation_id,candidate_id,coverage_status\n", encoding="utf-8"
            )
            candidate = {
                "candidate_id": "CAND-TEST", "atomic_obligation_id": "", "source_unit_id": "UNIT-1",
                "document": "docs/BLUEPRINT.md", "start_line": 1, "end_line": 1,
                "graph_node_ids": "", "review_reason": "Needs semantic review",
                "classification_confidence": "LOW", "source_excerpt": "Example source",
            }
            with (
                patch.object(coverage_builder, "PLAN", plan),
                patch.object(coverage_builder, "COVERAGE", root),
                patch.object(coverage_builder, "git_blob", return_value="pinned-plan-blob"),
                patch.object(coverage_builder, "graph_data", return_value=([], "0" * 64)),
            ):
                coverage_builder.build_package_index_and_traces([candidate], {}, "0" * 64)
            _, packages = coverage_builder.read_csv(root / "package-execution-index.csv")
            _, traces = coverage_builder.read_csv(root / "execution-trace.csv")
            _, gaps = coverage_builder.read_csv(root / "coverage-gap-register.csv")
        self.assertEqual(len(packages), 1)
        self.assertEqual(packages[0]["plan_heading_lines"], "")
        self.assertEqual(traces[0]["coverage_status"], "NOT_MAPPED_CANDIDATE")
        self.assertEqual(traces[0]["review_status"], "UNVERIFIED_SEMANTIC_MAPPING")
        self.assertEqual(gaps[0]["gap_type"], "PENDING_SEMANTIC_REVIEW")

    def test_csv_reader_rejects_missing_and_extra_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "short.csv"
            path.write_text("id,value\nA\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "missing value.*value"):
                coverage_builder.read_csv(path)
            path.write_text("id,value\nA,B,C\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "extra field"):
                coverage_builder.read_csv(path)

    def test_builder_main_publishes_a_complete_temp_generation(self):
        original_root = coverage_builder.ROOT
        graph_nodes, graph_digest = coverage_builder.graph_data()
        source_paths = [relative for _, relative in coverage_builder.SOURCES]
        plan_relative = coverage_builder.PLAN.relative_to(original_root)
        graph_relative = Path(coverage_builder.GRAPH_PATH)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target_coverage = root / "docs/audits/phase2-source-coverage"
            shutil.copytree(coverage_builder.COVERAGE, target_coverage)
            for relative in (*source_paths, str(plan_relative), str(graph_relative)):
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(original_root / relative, target)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            fake_run = subprocess.CompletedProcess(["python", "build_evidence_join_index.py"], 0, "", "")
            original_run = subprocess.run

            def run_external(command, *args, **kwargs):
                if any("build_evidence_join_index.py" in str(part) for part in command):
                    with (
                        patch.object(join, "ROOT", root),
                        patch.object(join, "COVERAGE", target_coverage),
                        patch.object(join, "GRAPH_PATH", root / graph_relative),
                    ):
                        join.publish_index(
                            target_coverage / "evidence-join-index.json", join.build()
                        )
                    return fake_run
                return original_run(command, *args, **kwargs)

            with (
                patch.object(coverage_builder, "ROOT", root),
                patch.object(coverage_builder, "COVERAGE", target_coverage),
                patch.object(coverage_builder, "PLAN", root / plan_relative),
                patch.object(coverage_builder, "graph_data", return_value=(
                    graph_nodes + [{"id": "graph-node-without-source-file"}], graph_digest
                )),
                patch.object(coverage_builder.subprocess, "run", side_effect=run_external),
                patch("sys.argv", ["build_and_validate.py"]),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                result = coverage_builder.main()
            self.assertEqual(result, 0)
            inventory = coverage_builder.read_csv(target_coverage / "source-inventory.csv")[1]
            candidates = coverage_builder.read_csv(target_coverage / "atomic-obligations.csv")[1]
            self.assertEqual(len(inventory), 1547)
            self.assertEqual(len(candidates), 1633)
            for name in (
                "execution-trace.csv", "package-execution-index.csv",
                "coverage-gap-register.csv", "validation-report.json",
                "semantic-validation-report.md",
            ):
                self.assertTrue((target_coverage / name).is_file(), name)
            report = json.loads((target_coverage / "validation-report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["counts"]["candidate_records"], 1633)
            previous_candidate_ids = {row["candidate_id"] for row in candidates}
            source_path = root / source_paths[0]
            original_source = source_path.read_text(encoding="utf-8")
            old_physical_lines = len(original_source.splitlines())
            source_path.write_text(
                original_source.rstrip("\n")
                + "\n\nA newly added, non-normative paragraph used to verify monotonic candidate IDs.\n"
                  "\n```python\nexample_value = 1\n```\n",
                encoding="utf-8",
            )
            new_physical_lines = len(source_path.read_text(encoding="utf-8").splitlines())
            unit_ledger_path = target_coverage / "source-unit-review-dispositions.csv"
            with unit_ledger_path.open(encoding="utf-8", newline="") as handle:
                unit_reader = csv.DictReader(handle)
                unit_fields, unit_rows = list(unit_reader.fieldnames), list(unit_reader)
            for unit_row in unit_rows:
                match = re.fullmatch(
                    rf"{re.escape(source_paths[0])}:(\d+)-(\d+) \(([^)]+)\)",
                    unit_row["source_evidence"],
                )
                if match and int(match.group(2)) == old_physical_lines:
                    unit_row["source_evidence"] = (
                        f"{source_paths[0]}:{match.group(1)}-{new_physical_lines} ({match.group(3)})"
                    )
            self.write_ledger(unit_ledger_path, unit_fields, unit_rows)
            appended_stdout = io.StringIO()
            with (
                patch.object(coverage_builder, "ROOT", root),
                patch.object(coverage_builder, "COVERAGE", target_coverage),
                patch.object(coverage_builder, "PLAN", root / plan_relative),
                patch.object(coverage_builder, "graph_data", return_value=(
                    graph_nodes + [{"id": "graph-node-without-source-file"}], graph_digest
                )),
                patch.object(coverage_builder.subprocess, "run", side_effect=run_external),
                patch("sys.argv", ["build_and_validate.py"]),
                contextlib.redirect_stdout(appended_stdout),
            ):
                appended_result = coverage_builder.main()
            self.assertEqual(appended_result, 0, appended_stdout.getvalue())
            appended_candidates = coverage_builder.read_csv(target_coverage / "atomic-obligations.csv")[1]
            appended_ids = {row["candidate_id"] for row in appended_candidates} - previous_candidate_ids
            self.assertEqual(len(appended_ids), 2)
            self.assertEqual(sum(candidate_id.startswith("BP-C-") for candidate_id in appended_ids), 1)
            self.assertEqual(sum(candidate_id.startswith("BP-CODE-") for candidate_id in appended_ids), 1)
            with unit_ledger_path.open(encoding="utf-8", newline="") as handle:
                unit_reader = csv.DictReader(handle)
                unit_fields, unit_rows = list(unit_reader.fieldnames), list(unit_reader)
            unit_rows = [row for row in unit_rows if row["source_unit_id"] != "BP-H-001"]
            self.write_ledger(unit_ledger_path, unit_fields, unit_rows)
            original_parse_sources = coverage_builder.parse_sources

            def omit_one_heading(path):
                parsed = original_parse_sources(path)
                if Path(path) == root / source_paths[0]:
                    parsed["headings"].pop(0)
                return parsed

            structural_stdout = io.StringIO()
            with (
                patch.object(coverage_builder, "ROOT", root),
                patch.object(coverage_builder, "COVERAGE", target_coverage),
                patch.object(coverage_builder, "PLAN", root / plan_relative),
                patch.object(coverage_builder, "parse_sources", side_effect=omit_one_heading),
                patch.object(coverage_builder, "graph_data", return_value=(
                    graph_nodes + [{"id": "graph-node-without-source-file"}], graph_digest
                )),
                patch.object(coverage_builder.subprocess, "run", side_effect=run_external),
                patch("sys.argv", ["build_and_validate.py"]),
                contextlib.redirect_stdout(structural_stdout),
            ):
                structural_result = coverage_builder.main()
            self.assertEqual(structural_result, 1)
            self.assertIn("nonblank line", structural_stdout.getvalue())
            self.assertIn("structural_errors", structural_stdout.getvalue())

    def test_script_entrypoint_reports_and_propagates_builder_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script = root / "docs/audits/phase2-source-coverage/build_and_validate.py"
            script.parent.mkdir(parents=True)
            shutil.copyfile(coverage_builder.__file__, script)
            (script.parent / "source-inventory.csv").write_text("id,id\nA,B\n", encoding="utf-8")
            (script.parent / "atomic-obligations.csv").write_text("candidate_id\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(script)], cwd=root, capture_output=True, text=True, check=False
            )
            reported = io.StringIO()
            previous_argv = sys.argv
            try:
                sys.argv = [str(script)]
                with contextlib.redirect_stderr(reported), self.assertRaises(ValueError):
                    source = Path(coverage_builder.__file__).read_text(encoding="utf-8")
                    namespace = {"__name__": "__main__", "__file__": str(script)}
                    exec(compile(source, str(coverage_builder.__file__), "exec"), namespace)
            finally:
                sys.argv = previous_argv
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ERROR: Malformed CSV header", result.stderr)
        self.assertIn("source-inventory.csv", result.stderr)
        self.assertIn("ERROR: Malformed CSV header", reported.getvalue())

    def test_check_only_requires_and_verifies_exact_baseline_fallback(self):
        original_root = coverage_builder.ROOT
        graph_nodes, graph_digest = coverage_builder.graph_data()
        source_paths = [relative for _, relative in coverage_builder.SOURCES]
        plan_relative = coverage_builder.PLAN.relative_to(original_root)
        baseline_prefix = f"{coverage_builder.BASELINE_COMMIT}:{coverage_builder.COVERAGE.relative_to(original_root)}"
        exact_inventory = subprocess.check_output(["git", "show", f"{baseline_prefix}/source-inventory.csv"], cwd=original_root)
        exact_candidates = subprocess.check_output(["git", "show", f"{baseline_prefix}/atomic-obligations.csv"], cwd=original_root)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target_coverage = root / "docs/audits/phase2-source-coverage"
            shutil.copytree(coverage_builder.COVERAGE, target_coverage)
            for relative in (*source_paths, str(plan_relative)):
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(original_root / relative, target)
            exact_inventory_path = root / "baseline-inventory.csv"
            exact_candidates_path = root / "baseline-candidates.csv"
            exact_inventory_path.write_bytes(exact_inventory)
            exact_candidates_path.write_bytes(exact_candidates)
            fake_run = subprocess.CompletedProcess(["git", "ls-files"], 0, b"", b"")
            original_check_output = subprocess.check_output

            def unavailable_git_show(command, *args, **kwargs):
                if (
                    len(command) > 1
                    and command[0] == "git"
                    and command[1] == "show"
                    and command[-1].endswith("atomic-obligations.csv")
                ):
                    raise subprocess.CalledProcessError(128, command)
                return original_check_output(command, *args, **kwargs)

            with (
                patch.object(coverage_builder, "ROOT", root),
                patch.object(coverage_builder, "COVERAGE", target_coverage),
                patch.object(coverage_builder, "PLAN", root / plan_relative),
                patch.object(coverage_builder, "graph_data", return_value=(graph_nodes, graph_digest)),
                patch.object(coverage_builder.subprocess, "check_output", side_effect=unavailable_git_show),
                patch.object(coverage_builder.subprocess, "run", return_value=fake_run),
                patch("sys.argv", ["build_and_validate.py", "--check-only"]),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                with patch.dict("os.environ", {}, clear=False):
                    import os
                    os.environ.pop("SHAHAB_BASELINE_SOURCE_INVENTORY", None)
                    os.environ.pop("SHAHAB_BASELINE_ATOMIC_OBLIGATIONS", None)
                    with self.assertRaisesRegex(RuntimeError, "Pinned baseline Git objects are missing"):
                        coverage_builder.main()
                with patch.dict("os.environ", {
                    "SHAHAB_BASELINE_SOURCE_INVENTORY": str(target_coverage / "source-inventory.csv"),
                    "SHAHAB_BASELINE_ATOMIC_OBLIGATIONS": str(target_coverage / "atomic-obligations.csv"),
                }, clear=False):
                    with self.assertRaisesRegex(RuntimeError, "Provided baseline files do not match"):
                        coverage_builder.main()
                with patch.dict("os.environ", {
                    "SHAHAB_BASELINE_SOURCE_INVENTORY": str(exact_inventory_path),
                    "SHAHAB_BASELINE_ATOMIC_OBLIGATIONS": str(exact_candidates_path),
                }, clear=False):
                    self.assertEqual(coverage_builder.main(), 0)

    def test_validate_outputs_accumulates_malformed_candidate_and_ledger_errors(self):
        source_files = [relative for _, relative in coverage_builder.SOURCES]
        plan_relative = coverage_builder.PLAN.relative_to(coverage_builder.ROOT)
        graph_nodes = coverage_builder.graph_data()[0]
        hashes = {}
        for relative in source_files:
            path = coverage_builder.ROOT / relative
            hashes[relative] = {
                "git_blob_sha": coverage_builder.git_blob(relative),
                "sha256": coverage_builder.sha256(path),
                "physical_lines": len(path.read_text(encoding="utf-8").splitlines()),
            }
        old_inventory = coverage_builder.read_csv(coverage_builder.COVERAGE / "source-inventory.csv")[1]
        old_candidates = coverage_builder.read_csv(coverage_builder.COVERAGE / "atomic-obligations.csv")[1]
        inventory = copy.deepcopy(old_inventory)
        candidates = copy.deepcopy(old_candidates)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target_coverage = root / "docs/audits/phase2-source-coverage"
            target_coverage.mkdir(parents=True)
            needed = (
                "package-execution-index.csv", "execution-trace.csv", "coverage-gap-register.csv",
                "package-semantic-evidence.csv", "evidence-join-index.json", "source-inventory.csv",
                "atomic-obligations.csv", "semantic-review-dispositions.csv",
                "atomic-obligation-dispositions.csv", "semantic-batch-progress.csv",
                "source-unit-review-dispositions.csv", "task-id-canonical-mapping.csv",
                "task-subtask-canonical-registry.csv", "extraction-manifest.json",
            )
            for name in needed:
                shutil.copyfile(coverage_builder.COVERAGE / name, target_coverage / name)
            for relative in (*source_files, str(plan_relative)):
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(coverage_builder.ROOT / relative, target)

            inventory[0]["source_unit_id"] = inventory[1]["source_unit_id"]
            inventory[0]["start_line"] = "999999"
            inventory[0]["graph_node_ids"] = "missing-graph-node"
            candidates[0]["candidate_id"] = candidates[1]["candidate_id"]
            candidates[0]["source_unit_id"] = "missing-source-unit"
            candidates[0]["parent_heading_id"] = "missing-heading"
            candidates[0]["normative_status"] = "INVALID_STATUS"
            candidates[0]["classification_suggestion"] = "INVALID_SUGGESTION"
            candidates[0]["graph_node_ids"] = "missing-graph-node"

            def read_rows(name):
                return coverage_builder.read_csv(target_coverage / name)

            def write_rows(name, fields, rows):
                with (target_coverage / name).open("w", encoding="utf-8", newline="") as handle:
                    writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
                    writer.writeheader()
                    writer.writerows(rows)

            fields, reviews = read_rows("semantic-review-dispositions.csv")
            atom_candidate_ids = {row.get("candidate_id") for row in read_rows("atomic-obligation-dispositions.csv")[1]}
            overwritten_candidate_ids = {old_candidates[0]["candidate_id"], old_candidates[1]["candidate_id"]}
            candidate_without_atom = next(
                row["candidate_id"] for row in old_candidates
                if row["candidate_id"] not in atom_candidate_ids
                and row["candidate_id"] not in overwritten_candidate_ids
            )
            reviews[0]["candidate_id"] = candidate_without_atom
            reviews[0]["source_evidence"] = "incorrect:999 (UNKNOWN)"
            reviews[0]["normative_status"] = "INVALID_STATUS"
            reviews[0]["atomicity_status"] = "DECOMPOSED"
            reviews[0].update({
                "semantic_disposition": "VERIFIED_PARTIAL",
                "normative_status": "NORMATIVE_APPROVED",
                "coverage_status": "VERIFIED_PARTIAL",
                "mapping_status": "UNMAPPED_GAP",
                "atomic_obligation_id": "SYNTHETIC-EXPLICIT-GAP",
                "plan_evidence": "PLAN:0",
                "related_packages": "UNKNOWN-PACKAGE",
                "requirement_ids": "REQ:UNKNOWN",
                "task_ids": "TASK:UNKNOWN",
                "ac_test_ids": "AC:UNKNOWN",
            })
            reviews.append(reviews[0].copy())
            reviews.pop()
            reviews.pop()
            reviews.append(reviews[0].copy())
            reviews.append({**reviews[0], "candidate_id": "ORPHAN_CANDIDATE"})
            reviewed_ids = {row["candidate_id"] for row in reviews}
            promoted = next(row for row in candidates if row["candidate_id"] not in reviewed_ids)
            promoted.update({"normative_status": "NORMATIVE_APPROVED", "review_status": "VERIFIED"})
            pending = next(
                row for row in candidates
                if row["candidate_id"] not in reviewed_ids and row is not promoted
            )
            pending.update({"normative_status": "NEEDS_REVIEW", "review_status": "REVIEW_REQUIRED"})
            write_rows("semantic-review-dispositions.csv", fields, reviews)
            fields, atoms = read_rows("atomic-obligation-dispositions.csv")
            atoms[0]["candidate_id"] = old_candidates[2]["candidate_id"]
            atoms[0]["atomic_obligation_id"] = "SYNTHETIC-DUPLICATE"
            atoms[1]["atomic_obligation_id"] = "SYNTHETIC-DUPLICATE"
            atoms[0]["source_evidence"] = "incorrect locator"
            atoms[0]["normalized_obligation"] = ""
            atoms[0]["normative_status"] = "INVALID_STATUS"
            atoms[0]["coverage_status"] = "VERIFIED_UNCOVERED"
            atoms[0]["mapping_status"] = "UNMAPPED_GAP"
            atoms[0]["plan_evidence"] = "not-a-locator"
            atoms[1].update({
                "coverage_status": "VERIFIED_COVERED", "mapping_status": "MAPPED",
                "related_packages": "", "requirement_ids": "", "task_ids": "",
                "ac_test_ids": "", "plan_evidence": "PLAN:999999",
            })
            atoms[2].update({
                "coverage_status": "VERIFIED_COVERED", "mapping_status": "MAPPED",
                "plan_evidence": f"PLAN:{1}", "requirement_ids": "REQ:NOT-IN-PLAN",
                "related_packages": "PKG:UNKNOWN", "task_ids": "TASK:UNKNOWN",
                "ac_test_ids": "AC:UNKNOWN",
            })
            atoms.append({**atoms[0], "atomic_obligation_id": "UNKNOWN-ATOM", "candidate_id": "UNKNOWN_CANDIDATE"})
            open_candidate = old_candidates[3]
            atoms.append({
                **atoms[0], "atomic_obligation_id": "OPEN-WITHOUT-REFERENCE",
                "candidate_id": open_candidate["candidate_id"],
                "source_evidence": f"{open_candidate['document']}:{open_candidate['start_line']} ({open_candidate['source_unit_id']})",
                "normalized_obligation": "Open decision", "normative_status": "NORMATIVE_OPEN_DECISION",
                "coverage_status": "OPEN_DECISION", "decision_reference": "",
            })
            write_rows("atomic-obligation-dispositions.csv", fields, atoms)
            source_unit_fields, source_units = read_rows("source-unit-review-dispositions.csv")
            matching_unit = next(
                row for row in source_units
                if any(item["source_unit_id"] == row["source_unit_id"] for item in inventory)
            )
            matching_unit["semantic_disposition"] = "INVALID_DISPOSITION"
            matching_unit["source_evidence"] = "wrong locator"
            matching_unit["unit_type"] = "INVALID_UNIT"
            source_units.append(source_units[0].copy())
            source_units.append({**source_units[0], "source_unit_id": "UNKNOWN_UNIT"})
            write_rows("source-unit-review-dispositions.csv", source_unit_fields, source_units)
            fields, batches = read_rows("semantic-batch-progress.csv")
            batches.extend([batches[0].copy(), {**batches[0], "candidate_id": "UNKNOWN_CANDIDATE"}])
            write_rows("semantic-batch-progress.csv", fields, batches)
            fields, packages = read_rows("package-execution-index.csv")
            package_task_id = next(
                item for item in coverage_builder.ID_RE.findall(
                    (root / plan_relative).read_text(encoding="utf-8")
                ) if item.startswith("TASK:CORE:")
            )
            valid_package_reference = next(
                (item for item in coverage_builder.ID_RE.findall((root / plan_relative).read_text(encoding="utf-8"))
                 if item.startswith("TC:RAG:") and item.endswith(("-P", "-N", "-B", "-F"))),
                package_task_id,
            )
            packages[0]["mentioned_task_subtask_ids"] = package_task_id
            packages[1]["mentioned_test_case_ids"] = valid_package_reference.rsplit("-", 1)[0]
            packages[2]["mentioned_test_case_ids"] = "TC:RAG:R01:999"
            write_rows("package-execution-index.csv", fields, packages)
            fields, task_mapping = read_rows("task-id-canonical-mapping.csv")
            task_mapping[0]["legacy_id"] = task_mapping[1]["legacy_id"]
            invalid_canonical_task = "TASK:CORE:" + "UNKNOWN:999"
            task_mapping[0]["canonical_id"] = invalid_canonical_task
            write_rows("task-id-canonical-mapping.csv", fields, task_mapping)
            fields, task_registry = read_rows("task-subtask-canonical-registry.csv")
            task_registry[0]["canonical_id"] = task_registry[1]["canonical_id"]
            subtask = next(row for row in task_registry if row["unit_type"] == "SUBTASK")
            subtask["parent_task_id"] = invalid_canonical_task
            write_rows("task-subtask-canonical-registry.csv", fields, task_registry)
            fields, reviews = read_rows("semantic-review-dispositions.csv")
            legacy_task_alias = "TASK:" + "C01:001"
            reviews[0]["task_ids"] = legacy_task_alias
            write_rows("semantic-review-dispositions.csv", fields, reviews)
            fields, atoms = read_rows("atomic-obligation-dispositions.csv")
            atoms[0]["task_ids"] = legacy_task_alias
            write_rows("atomic-obligation-dispositions.csv", fields, atoms)
            (root / "operational.md").write_text(
                f"Legacy {legacy_task_alias} and undefined {invalid_canonical_task} references.\n", encoding="utf-8"
            )
            fields, traces = read_rows("execution-trace.csv")
            verified_trace = next(row for row in traces if row["candidate_id"] == reviews[1]["candidate_id"])
            verified_trace.update({"coverage_status": "VERIFIED_COVERED", "review_status": "VERIFIED",
                                   "owner_package_candidates": "MISMATCH"})
            write_rows("execution-trace.csv", fields, traces)
            reviewed_unit = next(row for row in inventory if row["source_unit_id"] == matching_unit["source_unit_id"])
            reviewed_unit.update({"normative_status": "NEEDS_REVIEW", "coverage_status": "REVIEW_REQUIRED"})
            unit_id_counts = Counter(row["source_unit_id"] for row in inventory)
            clean_heading = next(
                row for row in inventory
                if row["unit_type"] == "HEADING" and unit_id_counts[row["source_unit_id"]] == 1
            )
            clean_heading_ledger = next(
                row for row in source_units if row["source_unit_id"] == clean_heading["source_unit_id"]
            )
            clean_heading_ledger.update({
                "unit_type": "HEADING", "semantic_disposition": "STRUCTURAL_SECTION_LOCATOR",
                "source_evidence": (
                    f"{clean_heading['document']}:{clean_heading['start_line']}-"
                    f"{clean_heading['end_line']} ({clean_heading['source_unit_id']})"
                ),
            })
            clean_heading.update({"normative_status": "NEEDS_REVIEW", "coverage_status": "REVIEW_REQUIRED"})
            write_rows("source-unit-review-dispositions.csv", source_unit_fields, source_units)

            with (
                patch.object(coverage_builder, "ROOT", root),
                patch.object(coverage_builder, "COVERAGE", target_coverage),
                patch.object(coverage_builder, "PLAN", root / plan_relative),
                patch.object(coverage_builder.subprocess, "run", return_value=subprocess.CompletedProcess(
                    ["git"], 0, b"operational.md\0", b""
                )),
            ):
                result = coverage_builder.validate_outputs(
                    old_inventory, old_candidates, inventory, candidates, hashes, graph_nodes, []
                )
                join_index_path = target_coverage / "evidence-join-index.json"
                valid_join_bytes = join_index_path.read_bytes()
                join_index_path.write_text("{invalid JSON", encoding="utf-8")
                invalid_join_result = coverage_builder.validate_outputs(
                    old_inventory, old_candidates, inventory, candidates, hashes, graph_nodes, []
                )
                self.assertEqual(invalid_join_result["evidence_join_index_integrity"]["result"], "FAIL")
                join_index_path.write_bytes(valid_join_bytes)
                (target_coverage / "task-id-canonical-mapping.csv").unlink()
                missing_mapping_result = coverage_builder.validate_outputs(
                    old_inventory, old_candidates, inventory, candidates, hashes, graph_nodes, []
                )
                (target_coverage / "task-subtask-canonical-registry.csv").unlink()
                missing_registry_result = coverage_builder.validate_outputs(
                    old_inventory, old_candidates, inventory, candidates, hashes, graph_nodes, []
                )
            for control in (
                "source_unit_id_uniqueness", "atomic_candidate_id_uniqueness",
                "source_line_ranges", "graph_node_references", "candidate_source_unit_references",
                "parent_heading_references", "classification_status_values",
                "classification_suggestion_values", "semantic_review_disposition_integrity",
                "atomic_obligation_ledger_integrity", "semantic_batch_ledger_integrity",
                "candidate_count_reconciliation", "heuristic_status_not_promoted",
                "no_unverified_mapping_marked_verified", "structural_source_unit_disposition_integrity",
            ):
                self.assertEqual(result[control]["result"], "FAIL", control)
            self.assertEqual(
                missing_registry_result["requirement_task_ac_test_references"]["result"], "FAIL"
            )
            self.assertEqual(
                missing_mapping_result["requirement_task_ac_test_references"]["result"], "FAIL"
            )

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

    def test_join_script_reports_controlled_cli_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script_dir = root / "docs/audits/phase2-source-coverage"
            script_dir.mkdir(parents=True)
            script = script_dir / "build_evidence_join_index.py"
            shutil.copyfile(join.__file__, script)
            for name in join.REQUIRED_COLUMNS:
                shutil.copyfile(join.COVERAGE / name, script_dir / name)
            (script_dir / "source-inventory.csv").write_text("wrong_header\nvalue\n", encoding="utf-8")
            stdout = io.StringIO()
            previous_argv = sys.argv
            try:
                sys.argv = [str(script)]
                source = Path(join.__file__).read_text(encoding="utf-8")
                namespace = {"__name__": "__main__", "__file__": str(script)}
                with contextlib.redirect_stdout(stdout), self.assertRaises(SystemExit) as raised:
                    exec(compile(source, str(join.__file__), "exec"), namespace)
            finally:
                sys.argv = previous_argv
        self.assertIn("source-inventory.csv", str(raised.exception))
        self.assertIn("source_unit_id", str(raised.exception))

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
            self._validate_records(records)

    def _validate_records(self, records):
        self.write_manifest(records)
        self.commit_manifest()
        return snapshot_validator.validate(self.manifest_path, self.root)

    def update_committed_fixture_artifact(self, relative, payload):
        target = self.root / relative
        target.write_bytes(payload)
        subprocess.run(["git", "add", relative], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "mutate snapshot test artifact"], cwd=self.root, check=True)
        self.commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.root, text=True).strip()
        self.pin_commit.stop()
        self.pin_commit = patch.object(snapshot_validator, "APPROVED_SOURCE_COMMIT", self.commit)
        self.pin_commit.start()
        self.addCleanup(self.pin_commit.stop)
        blob = subprocess.check_output(["git", "hash-object", str(target)], cwd=self.root, text=True).strip()
        record = next(item for item in self.records if item["path"] == relative)
        record.update(sha256=hashlib.sha256(payload).hexdigest(), size_bytes=len(payload), git_blob_sha=blob)
        self.fixture_data[relative] = payload
        self.write_manifest()
        self.commit_manifest()

    def add_optional_fixture_record(self, *, required_for_phase5=False):
        relative = "docs/optional-review.bin"
        target = self.root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = b"optional review artifact"
        target.write_bytes(payload)
        subprocess.run(["git", "add", relative], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "optional artifact fixture"], cwd=self.root, check=True)
        self.commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.root, text=True).strip()
        self.pin_commit.stop()
        self.pin_commit = patch.object(snapshot_validator, "APPROVED_SOURCE_COMMIT", self.commit)
        self.pin_commit.start()
        self.addCleanup(self.pin_commit.stop)
        record = {"path": relative, "sha256": hashlib.sha256(payload).hexdigest(),
                  "size_bytes": len(payload), "git_blob_sha": subprocess.check_output(
                      ["git", "hash-object", str(target)], cwd=self.root, text=True).strip(),
                  "role": "OPTIONAL_HUMAN_REVIEW", "required_for_phase5": required_for_phase5}
        values = self.records + [record]
        references = [item for item in values if item["role"] == "REQUIRED_REFERENCE_INPUT"]
        self.write_manifest(records=values, reference_inputs=references,
                            optional_human_review_artifacts=[record])
        self.commit_manifest()
        return record

    def test_path_and_git_tree_helpers_fail_closed(self):
        for value in (None, "", "/outside", "../outside", "a\\b"):
            with self.subTest(path=value), self.assertRaises(snapshot_validator.SnapshotValidationError):
                snapshot_validator.safe_relative_path(value, self.root)
        outside = Path(self.temporary.name).parent / "snapshot-outside-target"
        outside.mkdir(exist_ok=True)
        escape_link = self.root / "escape-link"
        escape_link.symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(snapshot_validator.SnapshotValidationError, "escapes repository"):
            snapshot_validator.safe_relative_path("escape-link/file", self.root)
        inside = self.root / "inside-target"
        inside.mkdir()
        inside_link = self.root / "inside-link"
        inside_link.symlink_to(inside, target_is_directory=True)
        with self.assertRaisesRegex(snapshot_validator.SnapshotValidationError, "symbolic link"):
            snapshot_validator.safe_relative_path("inside-link/file", self.root)

        for entry, message in ((b"", "absent from certified commit"),
                               (b"malformed-tree-entry", "malformed Git tree entry"),
                               (b"120000 blob " + b"0" * 40 + b"\tlink", "expected regular Git blob")):
            with self.subTest(entry=entry[:12]), patch.object(snapshot_validator, "git", return_value=entry):
                with self.assertRaisesRegex(snapshot_validator.SnapshotValidationError, message):
                    snapshot_validator._read_committed_blob(self.root, "HEAD", "artifact")

    def test_artifact_group_and_manifest_read_shapes_are_validated(self):
        for group in (*snapshot_validator.REQUIRED_GROUPS, *snapshot_validator.OPTIONAL_GROUPS):
            malformed = {name: [] for name in (*snapshot_validator.REQUIRED_GROUPS, *snapshot_validator.OPTIONAL_GROUPS)}
            malformed[group] = None
            with self.subTest(group=group), self.assertRaisesRegex(snapshot_validator.SnapshotValidationError, group):
                snapshot_validator.artifact_records(malformed)
        outside = self.root.parent / "outside-manifest.json"
        with self.assertRaisesRegex(snapshot_validator.SnapshotValidationError, "inside the repository"):
            snapshot_validator.validate(outside, self.root)
        for filename, content, message in (("bad.json", "{", "manifest unreadable"),
                                           ("root-list.json", "[]", "manifest root must be an object")):
            path = self.root / filename
            path.write_text(content, encoding="utf-8")
            with self.subTest(filename=filename), self.assertRaisesRegex(snapshot_validator.SnapshotValidationError, message):
                snapshot_validator.validate(path, self.root)
        with self.assertRaisesRegex(snapshot_validator.SnapshotValidationError, "manifest unreadable"):
            snapshot_validator.validate(self.root / "missing.json", self.root)

    def test_manifest_working_copy_mismatch_and_origin_failures(self):
        original = self.manifest_path.read_bytes()
        try:
            self.manifest_path.write_bytes(original + b" ")
            with self.assertRaisesRegex(snapshot_validator.SnapshotValidationError, "manifest working file differs"):
                snapshot_validator.validate(self.manifest_path, self.root)
        finally:
            self.manifest_path.write_bytes(original)

        original_git = snapshot_validator.git
        def unsupported_origin(root, *args):
            if args == ("remote", "get-url", "origin"):
                return b"https://example.invalid/not-the-approved-repository"
            return original_git(root, *args)
        with patch.object(snapshot_validator, "git", side_effect=unsupported_origin):
            with self.assertRaisesRegex(snapshot_validator.SnapshotValidationError, "origin does not identify"):
                snapshot_validator.validate(self.manifest_path, self.root)

        def unreadable_origin(root, *args):
            if args == ("remote", "get-url", "origin"):
                raise snapshot_validator.SnapshotValidationError("injected origin lookup failure")
            return original_git(root, *args)
        with patch.object(snapshot_validator, "git", side_effect=unreadable_origin):
            with self.assertRaisesRegex(snapshot_validator.SnapshotValidationError, "origin is missing or unreadable"):
                snapshot_validator.validate(self.manifest_path, self.root)

    def test_manifest_record_and_summary_integrity_checks(self):
        cases = [
            (lambda records: records[0].update(sha256="bad"), {}, "invalid SHA-256"),
            (lambda records: records[0].update(size_bytes=-1), {}, "invalid size_bytes"),
            (lambda records: records[0].update(git_blob_sha="0" * 40), {}, "Git blob SHA mismatch"),
            (lambda records: records[0].update(required_for_phase5=False), {}, "required input marked optional"),
            (lambda records: records[0].update(role="WRONG_ROLE"), {}, "role does not match"),
            (lambda records: None, {"artifact_hashes": {}}, "path set does not match artifact records"),
            (lambda records: None, {"graph_statistics": {}}, "graph_statistics do not reconcile"),
            (lambda records: None, {"mapping_statistics": {}}, "mapping_statistics do not reconcile"),
            (lambda records: None, {"source_coverage_statistics": {}}, "source_coverage_statistics do not reconcile"),
            (lambda records: None, {"decision_statistics": {"open_decisions": 134, "blocked_mappings": 134, "stage4_replay_records": -1}}, "Stage 4 replay record count"),
        ]
        for index, (edit, overrides, message) in enumerate(cases):
            with self.subTest(case=index):
                records = [dict(record) for record in self.records]
                edit(records)
                self.write_manifest(records, **overrides)
                self.commit_manifest()
                with self.assertRaisesRegex(snapshot_validator.SnapshotValidationError, message):
                    snapshot_validator.validate(self.manifest_path, self.root)

    def test_missing_manifest_artifact_sets_and_summary_map_shapes(self):
        records = [dict(record) for record in self.records]
        records.pop(0)
        self.write_manifest(records)
        self.commit_manifest()
        with self.assertRaisesRegex(snapshot_validator.SnapshotValidationError, "manifest missing required artifacts"):
            snapshot_validator.validate(self.manifest_path, self.root)

        records = [dict(record) for record in self.records]
        primary = next(record for record in records if record["role"] == "REQUIRED_PRIMARY_INPUT")
        primary["role"] = "REQUIRED_REFERENCE_INPUT"
        self.write_manifest(records)
        self.commit_manifest()
        with self.assertRaisesRegex(snapshot_validator.SnapshotValidationError, "primary input set"):
            snapshot_validator.validate(self.manifest_path, self.root)

        records = [dict(record) for record in self.records]
        reference = next(record for record in records if record["role"] == "REQUIRED_REFERENCE_INPUT")
        reference["role"] = "OPTIONAL_HUMAN_REVIEW"
        reference["required_for_phase5"] = False
        self.write_manifest(records,
                            reference_inputs=[record for record in records if record["role"] == "REQUIRED_REFERENCE_INPUT"],
                            optional_human_review_artifacts=[reference])
        self.commit_manifest()
        with self.assertRaisesRegex(snapshot_validator.SnapshotValidationError, "reference input set"):
            snapshot_validator.validate(self.manifest_path, self.root)

        manifest = self.write_manifest(artifact_sizes=None)
        self.commit_manifest()
        with self.assertRaisesRegex(snapshot_validator.SnapshotValidationError, "artifact_sizes must be an object"):
            snapshot_validator.validate(self.manifest_path, self.root)

    def test_validation_flags_decisions_and_payloads_fail_closed(self):
        graph_path = "docs/phase4/task-map-graph/task-map-graph.json"
        mapping_path = "docs/phase4/task-map-graph/task-map-mapping.json"
        graph = json.loads(self.fixture_data[graph_path])
        graph["validation"]["unique_node_ids"] = False
        self.update_committed_fixture_artifact(graph_path, json.dumps(graph, separators=(",", ":")).encode())
        with self.assertRaisesRegex(snapshot_validator.SnapshotValidationError, "validation is not PASS"):
            snapshot_validator.validate(self.manifest_path, self.root)

        graph["validation"]["unique_node_ids"] = True
        self.update_committed_fixture_artifact(graph_path, json.dumps(graph, separators=(",", ":")).encode())

        mapping = json.loads(self.fixture_data[mapping_path])
        mapping["open_decision_references"][0]["decision_status"] = "CLOSED"
        self.update_committed_fixture_artifact(mapping_path, json.dumps(mapping, separators=(",", ":")).encode())
        with self.assertRaisesRegex(snapshot_validator.SnapshotValidationError, "not all preserved as OPEN/BLOCKED"):
            snapshot_validator.validate(self.manifest_path, self.root)

    def test_remaining_statistics_and_immutable_hash_fail_closed(self):
        original = dict(snapshot_validator.IMMUTABLE_SHA256)
        wrong = {path: "0" * 64 for path in original}
        with patch.object(snapshot_validator, "IMMUTABLE_SHA256", wrong):
            with self.assertRaisesRegex(snapshot_validator.SnapshotValidationError, "immutable graph SHA-256"):
                snapshot_validator.validate(self.manifest_path, self.root)

        self.write_manifest(decision_statistics={"open_decisions": 133, "blocked_mappings": 134, "stage4_replay_records": 657})
        self.commit_manifest()
        with self.assertRaisesRegex(snapshot_validator.SnapshotValidationError, "decision_statistics do not reconcile"):
            snapshot_validator.validate(self.manifest_path, self.root)

    def test_optional_artifact_required_flag_is_enforced(self):
        record = self.add_optional_fixture_record(required_for_phase5=False)
        self.assertEqual(snapshot_validator.validate(self.manifest_path, self.root)["result"], "CERTIFIED_SNAPSHOT_VALID")
        record["required_for_phase5"] = True
        values = self.records + [record]
        references = [item for item in values if item["role"] == "REQUIRED_REFERENCE_INPUT"]
        self.write_manifest(records=values, reference_inputs=references,
                            optional_human_review_artifacts=[record])
        self.commit_manifest()
        with self.assertRaisesRegex(snapshot_validator.SnapshotValidationError, "optional/audit artifact marked required"):
            snapshot_validator.validate(self.manifest_path, self.root)

    def test_artifact_summary_value_must_match_record(self):
        hashes = {record["path"]: record["sha256"] for record in self.records}
        first = self.records[0]
        hashes[first["path"]] = "0" * 64
        self.write_manifest(artifact_hashes=hashes)
        self.commit_manifest()
        with self.assertRaisesRegex(snapshot_validator.SnapshotValidationError, "artifact summary maps disagree"):
            snapshot_validator.validate(self.manifest_path, self.root)

    def test_embedded_graph_payload_must_match_pinned_source(self):
        import base64
        import gzip
        graph_path = "docs/phase4/task-map-graph/task-map-graph.json"
        graph = json.loads(self.fixture_data[graph_path])
        graph["source_payloads"]["current_project_code_graph"]["data"] = base64.b64encode(
            gzip.compress(b"wrong graph", mtime=0)).decode("ascii")
        self.update_committed_fixture_artifact(graph_path, json.dumps(graph, separators=(",", ":")).encode())
        with self.assertRaisesRegex(snapshot_validator.SnapshotValidationError, "embedded snapshot does not match"):
            snapshot_validator.validate(self.manifest_path, self.root)

    def test_detects_artifact_changed_during_final_recheck(self):
        target = self.root / self.records[0]["path"]
        original_read_bytes = Path.read_bytes
        calls = 0
        def changed_on_second_read(path):
            nonlocal calls
            result = original_read_bytes(path)
            if path == target:
                calls += 1
                if calls == 2:
                    return result + b" changed during final read"
            return result
        with patch.object(Path, "read_bytes", changed_on_second_read):
            with self.assertRaisesRegex(snapshot_validator.SnapshotValidationError, "changed during snapshot validation"):
                snapshot_validator.validate(self.manifest_path, self.root)

    def test_snapshot_cli_executes_entrypoint_and_relative_manifest_path(self):
        source = Path(snapshot_validator.__file__).read_text(encoding="utf-8")
        source = source.replace("8ce742b640bbcbb87be5fc29f3a5a28d92593dec", self.commit)
        source = source.replace("phase4-45ed4ec10d34216cf935", "phase4-fixture")
        fixture_hashes = {
            "knowledge-graph/phase2-reference-docs/semantic/graph.json": "f16e684dc773e9bf053e51da2a0a37e3b5ffaf88809e1b5d37f8befbf69e1c93",
            "docs/phase4/task-map-graph/current-project-code-graph.json": "0a496833d1a58a6d07e58f3d5d2b59f2c0306a924d8573a687fc4067c549c982",
            "docs/phase4/task-map-graph/new-project-task-graph.json": "deb940949583007628dccb89de538c8f3b278aef1c6f99d1386f613f107fa0f7",
        }
        for path, pinned_hash in fixture_hashes.items():
            source = source.replace(pinned_hash, hashlib.sha256(self.fixture_data[path]).hexdigest())
        namespace = {"__name__": "__main__", "__file__": snapshot_validator.__file__}
        output = io.StringIO()
        with (patch.object(sys, "argv", ["validate_phase4_snapshot.py", "--manifest", "manifest.json", "--repo-root", str(self.root)]),
              contextlib.redirect_stdout(output), self.assertRaises(SystemExit) as exit_result):
            exec(compile(source, snapshot_validator.__file__, "exec"), namespace)
        self.assertEqual(exit_result.exception.code, 0)
        self.assertIn("CERTIFIED_SNAPSHOT_VALID", output.getvalue())

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

    def test_nonzero_git_resolution_and_ancestry_status_are_rejected(self):
        original_git = snapshot_validator.git
        def wrong_resolved_commit(root, *args):
            if len(args) == 3 and args[:2] == ("rev-parse", "--verify") and args[2].endswith("^{commit}"):
                return b"0" * 40
            return original_git(root, *args)
        with patch.object(snapshot_validator, "git", side_effect=wrong_resolved_commit):
            with self.assertRaisesRegex(snapshot_validator.SnapshotValidationError, "did not resolve exactly"):
                snapshot_validator.validate(self.manifest_path, self.root)

        original_run = snapshot_validator.subprocess.run
        def non_ancestor(command, *args, **kwargs):
            if command[:3] == ["git", "merge-base", "--is-ancestor"]:
                return subprocess.CompletedProcess(command, 1, stdout=b"", stderr=b"")
            return original_run(command, *args, **kwargs)
        with patch.object(snapshot_validator.subprocess, "run", side_effect=non_ancestor):
            with self.assertRaisesRegex(snapshot_validator.SnapshotValidationError, "does not contain the certified source commit"):
                snapshot_validator.validate(self.manifest_path, self.root)

    def test_second_symlink_check_detects_race_after_safe_resolution(self):
        target = self.root / self.records[0]["path"]
        original_is_symlink = Path.is_symlink
        observations = 0
        def racing_symlink(path):
            nonlocal observations
            if path == target:
                observations += 1
                if observations == 3:
                    return True
            return original_is_symlink(path)
        with patch.object(Path, "is_symlink", racing_symlink):
            with self.assertRaisesRegex(snapshot_validator.SnapshotValidationError, "symbolic links are not accepted"):
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
        relation["source_locator"] = "docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:999999"
        relation["plan_locator"] = relation["source_locator"]
        mapping["mappings"][0]["source_graph_refs"] = ["MISSING_REFERENCE"]
        decisions = {row["open_decision_id"]: row for row in mapping["open_decision_references"]}
        decisions["AO:BP-C-0291:01"]["mapping_status"] = "MAPPED"
        decisions["AO:BP-C-0294:01"]["affected_scope"]["plan_locators"] = []
        special = {row["open_decision_id"]: row for row in mapping["required_22_reference_review"]}
        special["AO:BP-C-0298:01"]["package_refs"] = []
        mapping["validation"]["semantic_replay_projection_sha256"] = replay.projection_digest(mapping)
        inputs = [mapping] + [
            replay.readj(replay.FILES[key])
            for key in ("task_graph", "current_code_graph", "reference_graph", "code_manifest")
        ]
        scope_ref = next(
            ref for ref in mapping["stage4_code_search_audit"]["search_scope_refs"]
            if ref not in replay.PARTIAL
        )
        next(node for node in inputs[1]["nodes"] if node["id"] == scope_ref)["plan_refs"] = ["invalid-locator"]
        output = io.StringIO()
        with (patch.object(replay, "readj", side_effect=inputs),
              patch.object(sys, "argv", ["replay_stage4.py", "--check-only"]),
              contextlib.redirect_stdout(output)):
            self.assertEqual(replay.main(), 1)
        self.assertIn("relation endpoint is not a Package/Task/Contract/Decision ref", output.getvalue())
        self.assertIn("relation endpoint aliases disagree", output.getvalue())
        self.assertIn("invalid relation source locator", output.getvalue())
        self.assertIn("mapping has non-existent reference Node MISSING_REFERENCE", output.getvalue())
        self.assertIn("special open-decision scope mismatch AO:BP-C-0291:01", output.getvalue())
        self.assertIn("special open-decision Plan Task evidence missing AO:BP-C-0294:01", output.getvalue())
        self.assertIn("special open-decision review crosswalk mismatch AO:BP-C-0298:01", output.getvalue())

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
            ({"task": ()}, {}, nodes, corpus, "missing or duplicate partial code IDs"),
            ({"task": ("code-a", "code-a")}, {"code-a": evidence["code-a"]}, nodes, corpus,
             "missing or duplicate partial code IDs"),
            (partial, {"code-a": evidence["code-a"]}, nodes, corpus, "missing.*code-b"),
            (partial, dict(evidence, extra=("a.py", 1)), nodes, corpus, "unexpected.*extra"),
            (partial, evidence, {"code-a": nodes["code-a"]}, corpus, "code ID/file mismatch"),
            (partial, evidence, nodes, {"a.py": corpus["a.py"]}, "evidence not found"),
            (partial, dict(evidence, **{"code-b": ("b.py", 2)}), nodes, corpus, "evidence not found"),
        ]
        for partial_data, files, code_nodes, sources, error in variants:
            with self.subTest(error=error), self.assertRaisesRegex(ValueError, error):
                replay.validate_partial_files(partial_data, files, code_nodes, sources)

    def test_partials_keep_pinned_code_locators(self):
        mapping = replay.readj(replay.FILES["mapping"])
        records = mapping["stage4_code_search_audit"]["records"]
        for record in records:
            ref = record["task_or_package_ref"]
            if ref in replay.PARTIAL:
                actual = {h["code_node_ref"]: (h["file"], h["line"]) for h in record["code_search_hits"]}
                self.assertEqual(actual, {code_id: replay.PARTIAL_FILES[code_id] for code_id in replay.PARTIAL[ref]})

    def test_build_search_rejects_missing_inputs_and_matches_exact_ids(self):
        source_manifest = replay.readj(replay.FILES["code_manifest"])
        paths = sorted(source_manifest)
        task_ref = "TASK:CORE:C01:001"
        other_ref = "TASK:CORE:C01:002"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plan_path = root / "plan.md"
            plan_path.write_text("# plan\n", encoding="utf-8")
            for relative in paths:
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(
                    task_ref + "\n" if relative == paths[0] else "pass\n", encoding="utf-8"
                )
            tg = {"nodes": [
                {"id": task_ref, "node_type": "TASK", "name": "Alpha Bravo Charlie",
                 "plan_refs": ["invalid-locator"]},
                {"id": other_ref, "node_type": "TASK", "name": "Other package task", "plan_refs": []},
            ]}
            graph = {"nodes": []}
            mapping = {"mappings": [{"task_ref": task_ref, "mapping_status": "NEW_IMPLEMENTATION"}]}
            audit = {"search_scope_refs": [task_ref], "records": []}
            with (
                patch.object(replay, "ROOT", root),
                patch.dict(replay.FILES, plan="plan.md"),
                patch.object(replay, "PARTIAL", {}),
                patch.object(replay, "PARTIAL_FILES", {}),
            ):
                with self.assertRaisesRegex(ValueError, "missing pinned corpus file missing.py"):
                    replay.build_search(mapping, tg, graph, {"missing.py": {}}, audit)
                with self.assertRaisesRegex(ValueError, "expected 347 pinned active-code files, got 0"):
                    replay.build_search(mapping, tg, graph, {}, audit)
                results, inventory, _ = replay.build_search(
                    mapping, tg, graph, source_manifest, audit
                )
                self.assertEqual(len(inventory), 347)
                self.assertEqual(results[0]["exact_canonical_or_alias_matches"][0]["matched_id"], task_ref)
                self.assertEqual(results[0]["exact_plan_title_matches"], [])
            partial_files = {"NODE": (paths[0], 1)}
            partial = {task_ref: ("NODE",)}
            code_graph = {"nodes": [{"id": "NODE", "source_file": paths[0]}]}
            partial_tg = {"nodes": [
                {"id": task_ref, "node_type": "TASK", "name": "Partial task", "plan_refs": ["plan.md:1"]},
                tg["nodes"][1],
            ]}
            with (
                patch.object(replay, "ROOT", root),
                patch.dict(replay.FILES, plan="plan.md"),
                patch.object(replay, "PARTIAL", partial),
                patch.object(replay, "PARTIAL_FILES", partial_files),
            ):
                with self.assertRaisesRegex(ValueError, "missing partial mapping search scope or Plan evidence"):
                    replay.build_search(
                        mapping, partial_tg, code_graph, source_manifest,
                        {"search_scope_refs": [other_ref], "records": []},
                    )

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

    def test_mapping_stage_creation_failure_preserves_previous_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "mapping.json"
            previous = b"previous mapping bytes"
            target.write_bytes(previous)
            with patch.object(replay, "ROOT", Path(temporary)), patch.object(
                replay.tempfile, "NamedTemporaryFile", side_effect=OSError("injected stage creation failure")
            ):
                with self.assertRaisesRegex(OSError, "injected stage creation failure"):
                    replay.writej(Path("mapping.json"), {"mapping_id": "synthetic"})
            self.assertEqual(target.read_bytes(), previous)
            self.assertEqual(list(target.parent.iterdir()), [target])

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

    def test_write_code_search_rejects_inventory_drift_after_search(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "mapping.json"
            original = (replay.ROOT / replay.FILES["mapping"]).read_bytes()
            target.write_bytes(original)
            mapping = json.loads(original)
            mapping["stage4_code_search_audit"]["inventory_sha256"] = "0" * 64
            mapping["validation"]["semantic_replay_projection_sha256"] = replay.projection_digest(mapping)
            inputs = [mapping] + [
                replay.readj(replay.FILES[key])
                for key in ("task_graph", "current_code_graph", "reference_graph", "code_manifest")
            ]
            output = io.StringIO()
            with (
                patch.dict(replay.FILES, mapping=target),
                patch.object(replay, "readj", side_effect=inputs),
                patch.object(sys, "argv", ["replay_stage4.py", "--write-code-search"]),
                contextlib.redirect_stdout(output),
            ):
                result = replay.main()
            self.assertEqual(result, 1)
            self.assertIn("pinned 347-file code inventory changed", output.getvalue())
            self.assertNotIn('"write": "PASS"', output.getvalue())
            self.assertEqual(target.read_bytes(), original)

    def test_successful_code_search_write_isolated_from_certified_mapping(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "mapping.json"
            original = (replay.ROOT / replay.FILES["mapping"]).read_bytes()
            target.write_bytes(original)
            output = io.StringIO()
            with (
                patch.dict(replay.FILES, mapping=target),
                patch.object(sys, "argv", ["replay_stage4.py", "--write-code-search"]),
                contextlib.redirect_stdout(output),
            ):
                self.assertEqual(replay.main(), 0)
            written = json.loads(target.read_text(encoding="utf-8"))
        self.assertIn('"write": "PASS"', output.getvalue())
        self.assertEqual(len(written["stage4_code_search_audit"]["records"]), 657)
        self.assertEqual(len(written["open_decision_references"]), 134)
        self.assertTrue(all(item.get("decision_status", "OPEN") == "OPEN" for item in written["open_decision_references"]))
        self.assertTrue(all(item["mapping_status"] == "BLOCKED" for item in written["open_decision_references"]))

    def test_replay_script_reports_missing_input_as_controlled_failure(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            script = root / "docs/phase4/task-map-graph/replay_stage4.py"
            script.parent.mkdir(parents=True)
            previous_argv = sys.argv
            try:
                sys.argv = [str(script), "--check-only"]
                namespace = {"__name__": "__main__", "__file__": str(script)}
                source = Path(replay.__file__).read_text(encoding="utf-8")
                with self.assertRaises(SystemExit) as raised:
                    exec(compile(source, str(replay.__file__), "exec"), namespace)
            finally:
                sys.argv = previous_argv
        self.assertIn("FAIL:", str(raised.exception))
        self.assertIn("task-map-mapping.json", str(raised.exception))


if __name__ == "__main__":
    unittest.main(verbosity=2)
