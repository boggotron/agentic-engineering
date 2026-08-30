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
    def run_harness(self, results: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, RUNNER, "--results", results, "--json"], text=True, capture_output=True, check=False)

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


if __name__ == "__main__":
    unittest.main()
