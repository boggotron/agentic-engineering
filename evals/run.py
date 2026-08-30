#!/usr/bin/env python3
"""Score portable behavioral-evaluation observations with only the stdlib."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read JSON from {path}: {error}") from error


def score(scenarios: dict[str, dict[str, Any]], results: dict[str, Any]) -> dict[str, Any]:
    observations = results.get("observations")
    if not isinstance(observations, list):
        raise ValueError("results must contain an observations list")

    seen: set[str] = set()
    semantic_total = semantic_passed = 0
    mechanics_recorded = 0
    details = []
    for observation in observations:
        if not isinstance(observation, dict) or not isinstance(observation.get("scenario"), str):
            raise ValueError("every observation must be an object with a scenario id")
        scenario_id = observation["scenario"]
        if scenario_id not in scenarios:
            raise ValueError(f"unknown scenario: {scenario_id}")
        if scenario_id in seen:
            raise ValueError(f"duplicate scenario: {scenario_id}")
        seen.add(scenario_id)
        semantic = observation.get("semantic")
        if not isinstance(semantic, dict):
            raise ValueError(f"{scenario_id}: semantic must be an object of boolean checks")
        expected = [check["id"] for check in scenarios[scenario_id]["semantic_checks"]]
        if set(semantic) != set(expected) or not all(isinstance(semantic[key], bool) for key in expected):
            raise ValueError(f"{scenario_id}: semantic checks must exactly match: {', '.join(expected)}")
        passed = sum(semantic.values())
        semantic_passed += passed
        semantic_total += len(expected)
        mechanics = observation.get("host_mechanics", {})
        if not isinstance(mechanics, dict):
            raise ValueError(f"{scenario_id}: host_mechanics must be an object when supplied")
        mechanics_recorded += len(mechanics)
        details.append({"scenario": scenario_id, "semantic_passed": passed, "semantic_total": len(expected), "host_mechanics": mechanics})

    missing = set(scenarios) - seen
    if missing:
        raise ValueError(f"missing scenarios: {', '.join(sorted(missing))}")
    if len(seen) != len(scenarios):
        raise ValueError("observations do not match the scenario set")
    return {
        "semantic": {"passed": semantic_passed, "total": semantic_total, "pass_rate": 100 * semantic_passed / semantic_total},
        "host_mechanics": {"recorded_observations": mechanics_recorded, "note": "Informational only; mechanics never affect semantic compliance."},
        "scenarios": details,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, required=True, help="JSON observations to score")
    parser.add_argument("--scenarios", type=Path, default=Path(__file__).with_name("scenarios.json"))
    parser.add_argument("--json", action="store_true", help="emit the complete report as JSON")
    args = parser.parse_args()
    try:
        catalog = load_json(args.scenarios)
        scenarios = {item["id"]: item for item in catalog["scenarios"]}
        report = score(scenarios, load_json(args.results))
    except (KeyError, TypeError, ValueError) as error:
        parser.error(str(error))
    target = float(catalog["target_semantic_pass_rate"])
    passed = report["semantic"]["pass_rate"] >= target
    report["target_semantic_pass_rate"] = target
    report["passed"] = passed
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        semantic = report["semantic"]
        print(f"Semantic compliance: {semantic['passed']}/{semantic['total']} ({semantic['pass_rate']:.1f}%)")
        print(f"Target: >= {target:.1f}% — {'PASS' if passed else 'FAIL'}")
        print(f"Host mechanics: {report['host_mechanics']['recorded_observations']} observations recorded (informational; not scored)")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
