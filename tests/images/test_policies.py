"""Negative release/security cases prevent accidental publication eligibility."""

import copy
import unittest

from release_policy import REQUIRED, validate_gates, validate_image_evidence, validate_request
from security_gate import assess

SHA = "a" * 40
IMAGE = "sha256:" + "b" * 64


def gates():
    runs, jobs = [], {}
    for number, (path, names) in enumerate(REQUIRED.items(), 1):
        runs.append(
            {
                "id": number,
                "path": path,
                "head_sha": SHA,
                "head_branch": "main",
                "event": "push",
                "status": "completed",
                "conclusion": "success",
                "run_attempt": 1,
            }
        )
        jobs[number] = [
            {"name": name, "head_sha": SHA, "status": "completed", "conclusion": "success"} for name in names
        ]
    return runs, jobs


class ReleasePolicyTests(unittest.TestCase):
    def test_explicit_main_ancestor_with_seven_successes(self):
        validate_request("workflow_dispatch", "refs/heads/main", "v1.2.3", SHA, SHA, "ahead")
        self.assertEqual(len(validate_gates(SHA, *gates())), 4)

    def test_bad_trigger_ref_version_sha_or_ancestry(self):
        valid = ["workflow_dispatch", "refs/heads/main", "v1.2.3", SHA, SHA, "identical"]
        changes = [
            (0, "pull_request"),
            (0, "push"),
            (1, "refs/heads/other"),
            (1, "refs/tags/v1.2.3"),
            (2, "latest"),
            (2, "v01.2.3"),
            (2, "v1.2.3-rc1"),
            (2, "v1.2.3\n"),
            (2, "../main"),
            (3, "short"),
            (4, "b" * 40),
            (5, "behind"),
            (5, "diverged"),
        ]
        for index, value in changes:
            with self.subTest(index=index, value=value), self.assertRaises(ValueError):
                candidate = valid.copy()
                candidate[index] = value
                validate_request(*candidate)

    def test_missing_failed_pending_cancelled_skipped_job_or_other_sha_blocks(self):
        for conclusion in ("failure", "cancelled", "skipped", None):
            runs, jobs = gates()
            jobs[1][0]["conclusion"] = conclusion
            with self.subTest(conclusion=conclusion), self.assertRaises(ValueError):
                validate_gates(SHA, runs, jobs)
        for field, value in [("head_sha", "b" * 40), ("status", "in_progress")]:
            runs, jobs = gates()
            jobs[1][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_gates(SHA, runs, jobs)
        runs, jobs = gates()
        jobs[1].pop()
        with self.assertRaises(ValueError):
            validate_gates(SHA, runs, jobs)
        with self.assertRaises(ValueError):
            validate_gates(SHA, runs[:-1], jobs)

    def test_newer_failed_run_cannot_reuse_old_success(self):
        runs, jobs = gates()
        newer = copy.deepcopy(runs[0])
        newer.update(id=99, conclusion="failure")
        with self.assertRaises(ValueError):
            validate_gates(SHA, runs + [newer], jobs)

    def test_pr_success_cannot_substitute_main_success(self):
        runs, jobs = gates()
        runs[0]["event"] = "pull_request"
        with self.assertRaises(ValueError):
            validate_gates(SHA, runs, jobs)

    def test_old_green_job_without_matching_scan_smoke_and_provenance_is_rejected(self):
        other = "sha256:" + "c" * 64
        summary = {
            "sourceSha": SHA,
            "status": "passed",
            "images": [
                {"name": n, "imageId": i, "counts": {"HIGH": 0, "CRITICAL": 0}, "buildDigest": i}
                for n, i in zip(("api", "web"), (IMAGE, other), strict=True)
            ],
        }
        smoke = {"sourceSha": SHA, "status": "passed", "imageIds": [IMAGE, other]}
        builds = [
            {"containerimage.config.digest": i, "buildx.build.provenance": {"materials": []}} for i in (IMAGE, other)
        ]
        self.assertEqual(len(validate_image_evidence(SHA, summary, smoke, builds)), 2)
        for mutation in ("missing", "sha", "high", "image", "provenance"):
            a, b, c = copy.deepcopy((summary, smoke, builds))
            if mutation == "missing":
                a = {}
            elif mutation == "sha":
                a["sourceSha"] = "b" * 40
            elif mutation == "high":
                a["images"][0]["counts"]["HIGH"] = 1
            elif mutation == "image":
                b["imageIds"].reverse()
            else:
                c[0]["buildx.build.provenance"] = {}
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                validate_image_evidence(SHA, a, b, c)


class ScanPolicyTests(unittest.TestCase):
    def report(self):
        return {
            "ArtifactType": "container_image",
            "Metadata": {"ImageID": IMAGE, "OS": {"Family": "debian"}},
            "Results": [{"Class": "os-pkgs", "Packages": [{"Name": "example"}], "Vulnerabilities": []}],
        }

    def test_clean_and_all_severities_counted_including_unfixed(self):
        report = self.report()
        self.assertEqual(assess(report, IMAGE)["HIGH"], 0)
        report["Results"][0]["Vulnerabilities"] = [{"Severity": s} for s in ("HIGH", "CRITICAL", "MEDIUM")]
        counts = assess(report, IMAGE)
        self.assertEqual((counts["HIGH"], counts["CRITICAL"], counts["MEDIUM"]), (1, 1, 1))

    def test_missing_inventory_unknown_os_eol_wrong_id_and_malformed_fail_closed(self):
        for mutation in ("empty", "id", "os", "eol", "severity"):
            report = self.report()
            if mutation == "empty":
                report["Results"] = []
            elif mutation == "id":
                report["Metadata"]["ImageID"] = "wrong"
            elif mutation == "os":
                report["Metadata"]["OS"] = {}
            elif mutation == "eol":
                report["Metadata"]["OS"]["EOSL"] = True
            else:
                report["Results"][0]["Vulnerabilities"] = [{"Severity": "invented"}]
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                assess(report, IMAGE)


if __name__ == "__main__":
    unittest.main()
