"""Exact historical evidence codec; PostgreSQL transaction proof lives separately."""

import copy
import unittest
from dataclasses import replace
from decimal import Decimal

from pydantic import ValidationError

from backend.app.data_pipeline.application.prepare_import import prepare_import_manifest
from backend.app.data_pipeline.domain.publication import calculate_catalogue_diff
from backend.app.data_pipeline.infrastructure.operations_codec import (
    decode_diff,
    decode_preparation,
    encode_diff,
    encode_preparation,
)
from backend.tests.test_internal_data_operations import manifest


class OperationsEvidenceTests(unittest.TestCase):
    def test_exact_decimal_raw_provenance_and_immutable_round_trip(self):
        plan = prepare_import_manifest(
            source_file_sha256="a" * 64,
            parser_version="v1",
            rows=manifest(interestRate="18.25 درصد", maxAmount="نامشخص"),
        )
        encoded = encode_preparation(plan)
        restored = decode_preparation(encoded, source_hash="a" * 64, parser_version="v1")
        self.assertEqual(restored, plan)
        self.assertEqual(restored.accepted_rows[0].variables["interestRate"].numeric_value, Decimal("18.25"))
        self.assertEqual(restored.accepted_rows[0].variables["maxAmount"].raw, "نامشخص")
        with self.assertRaises(TypeError):
            restored.accepted_rows[0].variables["other"] = None
        diff = calculate_catalogue_diff((), plan.accepted_rows)
        self.assertEqual(decode_diff(encode_diff(diff)), diff)

    def test_dirty_plan_and_invalid_hash_evidence_survives(self):
        rows = (*manifest(), *manifest())
        plan = prepare_import_manifest(source_file_sha256="bad", parser_version="v1", rows=rows)
        self.assertFalse(plan.is_publishable_candidate)
        self.assertEqual(decode_preparation(encode_preparation(plan), source_hash="bad", parser_version="v1"), plan)
        rejected = prepare_import_manifest(
            source_file_sha256="a" * 64, parser_version="v1", rows=(replace(manifest()[0], lender_name=None),)
        )
        self.assertEqual(
            decode_preparation(encode_preparation(rejected), source_hash="a" * 64, parser_version="v1"), rejected
        )

    def test_unknown_schema_extra_fields_and_nonfinite_decimal_fail_closed(self):
        plan = prepare_import_manifest(source_file_sha256="a" * 64, parser_version="v1", rows=manifest())
        payload = encode_preparation(plan)
        for change in ({"schema_version": 2}, {"client_role": "admin"}):
            with self.assertRaises(ValidationError):
                decode_preparation({**payload, **change}, source_hash="a" * 64, parser_version="v1")
        modified = copy.deepcopy(payload)
        modified["accepted_rows"][0]["variables"]["interestRate"]["numeric_value"] = "NaN"
        with self.assertRaises(ValidationError):
            decode_preparation(modified, source_hash="a" * 64, parser_version="v1")
