#!/usr/bin/env python3
"""Regression tests for the behavioral-evaluation harness."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parent
RUNNER = ROOT / "run.py"
COMPLIANT = ROOT / "examples" / "compliant.json"


class BehavioralEvalTests(unittest.TestCase):
    def run_harness(self, results: Path, scenarios: Path | None = None) -> subprocess.CompletedProcess[str]:
        command = [sys.executable, RUNNER, "--results", results, "--json"]
        if scenarios is not None:
            command.extend(["--scenarios", str(scenarios)])
        return subprocess.run(command, text=True, capture_output=True, check=False)

    def write_json(self, directory: str, name: str, data: object) -> Path:
        path = Path(directory) / name
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_all_ten_scenarios_pass_at_one_hundred_percent(self) -> None:
        result = self.run_harness(COMPLIANT)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["semantic"], {"passed": 30, "total": 30, "pass_rate": 100.0})
        self.assertTrue(report["passed"])
        self.assertEqual(len(report["scenarios"]), 10)

    def test_mechanics_do_not_change_semantic_threshold(self) -> None:
        data = json.loads(COMPLIANT.read_text(encoding="utf-8"))
        for observation in data["observations"]:
            observation["host_mechanics"] = {"implementation": "different host detail"}
        with tempfile.TemporaryDirectory() as directory:
            results = Path(directory) / "observations.json"
            results.write_text(json.dumps(data), encoding="utf-8")
            result = self.run_harness(results)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)["passed"])

    def test_below_ninety_percent_fails(self) -> None:
        data = json.loads(COMPLIANT.read_text(encoding="utf-8"))
        for observation in data["observations"][:4]:
            first_check = next(iter(observation["semantic"]))
            observation["semantic"][first_check] = False
        with tempfile.TemporaryDirectory() as directory:
            results = Path(directory) / "observations.json"
            results.write_text(json.dumps(data), encoding="utf-8")
            result = self.run_harness(results)
        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["semantic"]["pass_rate"], 86.66666666666667)
        self.assertFalse(report["passed"])

    def test_exactly_ninety_percent_passes(self) -> None:
        data = json.loads(COMPLIANT.read_text(encoding="utf-8"))
        for observation in data["observations"][:3]:
            observation["semantic"][next(iter(observation["semantic"]))] = False
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_harness(self.write_json(directory, "observations.json", data))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["semantic"]["pass_rate"], 90.0)

    def test_incomplete_and_duplicate_results_are_clear_errors(self) -> None:
        data = json.loads(COMPLIANT.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as directory:
            incomplete = self.write_json(directory, "incomplete.json", {"observations": data["observations"][:-1]})
            incomplete_result = self.run_harness(incomplete)
            duplicate = self.write_json(directory, "duplicate.json", {"observations": data["observations"] + [data["observations"][0]]})
            duplicate_result = self.run_harness(duplicate)
        self.assertEqual(incomplete_result.returncode, 2)
        self.assertIn("missing scenarios", incomplete_result.stderr)
        self.assertNotIn("Traceback", incomplete_result.stderr)
        self.assertEqual(duplicate_result.returncode, 2)
        self.assertIn("duplicate scenario", duplicate_result.stderr)
        self.assertNotIn("Traceback", duplicate_result.stderr)

    def test_malformed_results_root_is_a_clear_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_harness(self.write_json(directory, "malformed.json", []))
        self.assertEqual(result.returncode, 2)
        self.assertIn("results must be a JSON object", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_invalid_catalog_is_a_clear_error(self) -> None:
        data = json.loads(COMPLIANT.read_text(encoding="utf-8"))
        invalid_catalog = {"target_semantic_pass_rate": 90, "scenarios": [{"id": "one", "semantic_checks": []}]}
        with tempfile.TemporaryDirectory() as directory:
            results = self.write_json(directory, "observations.json", data)
            catalog = self.write_json(directory, "catalog.json", invalid_catalog)
            result = self.run_harness(results, catalog)
        self.assertEqual(result.returncode, 2)
        self.assertIn("semantic_checks must be a non-empty list", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_duplicate_catalog_scenario_is_a_clear_error(self) -> None:
        data = json.loads(COMPLIANT.read_text(encoding="utf-8"))
        duplicate_catalog = {"target_semantic_pass_rate": 90, "scenarios": [
            {"id": "one", "semantic_checks": [{"id": "check"}]},
            {"id": "one", "semantic_checks": [{"id": "other-check"}]}
        ]}
        with tempfile.TemporaryDirectory() as directory:
            results = self.write_json(directory, "observations.json", data)
            catalog = self.write_json(directory, "catalog.json", duplicate_catalog)
            result = self.run_harness(results, catalog)
        self.assertEqual(result.returncode, 2)
        self.assertIn("duplicate catalog scenario: one", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
