#!/usr/bin/env python3
"""Validate and score a RateMySkill audit using only the standard library."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "1"
POLICY_VERSION = "2"
MAX_INPUT_BYTES = 1_048_576
MAX_DIMENSIONS = 32
MAX_EVIDENCE = 512

MODES = {
    "skill-user",
    "staff-agent-engineer",
    "agent-engineer",
    "red-team",
    "adversarial",
    "marketplace-curator",
    "oral-defense",
}
PUBLISH_THRESHOLDS = {
    "local-draft": Decimal("50"),
    "team-shared": Decimal("65"),
    "public-marketplace": Decimal("75"),
    "privileged-production": Decimal("85"),
    "high-stakes": Decimal("90"),
}
VERIFICATION_FACTORS = {
    "verified": Decimal("1"),
    "partial": Decimal("0.5"),
    "unverified": Decimal("0"),
}
EVIDENCE_KINDS = {
    "runtime",
    "test",
    "install",
    "static-analysis",
    "manifest",
    "reference",
    "dependency",
    "log",
    "trace",
    "document",
    "claim",
}
EVIDENCE_RESULTS = {"pass", "fail", "mixed", "inconclusive"}
RUNTIME_LEVELS = {"full", "partial", "static", "none"}
SELECTION_LEVELS = {"tested", "partial", "claimed", "none"}
INSTALL_LEVELS = {"tested", "partial", "claimed", "none"}
RUNTIME_CONFIDENCE_CAP = {"full": "A", "partial": "B", "static": "C", "none": "D"}
SELECTION_CONFIDENCE_CAP = {"tested": "A", "partial": "B", "claimed": "C", "none": "D"}
INSTALL_CONFIDENCE_CAP = {"tested": "A", "partial": "B", "claimed": "C", "none": "D"}
CONFIDENCE_SCORE_CAP = {
    "A": Decimal("100"),
    "B": Decimal("89"),
    "C": Decimal("69"),
    "D": Decimal("49"),
}
CONFIDENCE_ORDER = {"A": 0, "B": 1, "C": 2, "D": 3}
PUBLIC_EVIDENCE_CAP = Decimal("69")
TEAM_EVIDENCE_CAP = Decimal("64")

# These are vetoes rather than ordinary dimensions: a high average cannot hide one.
SAFETY_GATES = {
    "dangerous-trigger-overreach": Decimal("39"),
    "untrusted-instruction-execution": Decimal("39"),
    "unauthorized-side-effect": Decimal("39"),
    "secret-or-data-exfiltration": Decimal("39"),
    "uncontrolled-code-execution": Decimal("39"),
    "hidden-network-or-telemetry": Decimal("39"),
    "fabricated-success-or-evidence": Decimal("39"),
    "broken-core-package": Decimal("39"),
    "license-or-provenance-breach": Decimal("39"),
}

RUNTIME_EVIDENCE_KINDS = {"runtime", "test", "trace"}
SELECTION_EVIDENCE_KINDS = {"test", "log", "trace"}
INSTALL_EVIDENCE_KINDS = {"install", "runtime", "test", "log", "trace"}
REFERENCE_EVIDENCE_KINDS = {"reference", "manifest", "runtime", "test"}
RETEST_EVIDENCE_KINDS = {
    "runtime",
    "test",
    "static-analysis",
    "manifest",
    "reference",
    "dependency",
    "trace",
}

# Higher distribution targets require these exact checks. Values restrict the
# evidence kinds that can support a passing status; generic prose cannot stand
# in for an exercised authority boundary or an independent review artifact.
PRIVILEGED_REQUIRED_CHECKS = {
    "sandboxed-authority-and-side-effects": {"runtime", "test", "trace"},
}
HIGH_STAKES_REQUIRED_CHECKS = {
    **PRIVILEGED_REQUIRED_CHECKS,
    "independent-domain-review": {"document", "test"},
    "human-control": {"runtime", "test", "trace"},
    "auditability": {"runtime", "test", "log", "trace"},
    "incident-response": {"runtime", "test", "document", "trace"},
}
TARGET_REQUIRED_CHECKS = {
    "local-draft": {},
    "team-shared": {},
    "public-marketplace": {},
    "privileged-production": PRIVILEGED_REQUIRED_CHECKS,
    "high-stakes": HIGH_STAKES_REQUIRED_CHECKS,
}


class ValidationError(Exception):
    def __init__(self, path: str, message: str) -> None:
        super().__init__(message)
        self.path = path
        self.message = message


class JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        emit_error("argument_error", "$", message)
        raise SystemExit(2)


def emit_error(code: str, path: str, message: str) -> None:
    payload = {"error": {"code": code, "message": message, "path": path}, "ok": False}
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True), file=sys.stderr)


def reject_constant(value: str) -> None:
    raise ValueError(f"non-finite number {value} is not allowed")


def load_payload(path: Path) -> Any:
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise ValidationError("$", f"cannot read input file: {exc.strerror or exc}") from exc
    if size > MAX_INPUT_BYTES:
        raise ValidationError("$", f"input exceeds {MAX_INPUT_BYTES} bytes")
    try:
        return json.loads(path.read_text(encoding="utf-8"), parse_constant=reject_constant)
    except UnicodeDecodeError as exc:
        raise ValidationError("$", f"input must be UTF-8: {exc}") from exc
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise ValidationError("$", f"invalid JSON: {exc}") from exc


def require_object(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError(path, "must be an object")
    return value


def require_list(value: Any, path: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValidationError(path, "must be an array")
    return value


def require_string(value: Any, path: str, allowed: set[str] | None = None) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(path, "must be a non-empty string")
    if allowed is not None and value not in allowed:
        raise ValidationError(path, f"must be one of {sorted(allowed)}; received {value!r}")
    return value


def require_bool(value: Any, path: str) -> bool:
    if type(value) is not bool:
        raise ValidationError(path, "must be true or false")
    return value


def require_int(value: Any, path: str, minimum: int, maximum: int) -> int:
    if type(value) is not int:
        raise ValidationError(path, f"must be an integer between {minimum} and {maximum}")
    if value < minimum or value > maximum:
        raise ValidationError(path, f"must be an integer between {minimum} and {maximum}; received {value}")
    return value


def reject_unknown(obj: dict[str, Any], allowed: set[str], path: str) -> None:
    unknown = sorted(set(obj) - allowed)
    if unknown:
        raise ValidationError(path, f"unexpected field(s): {', '.join(unknown)}")


def require_fields(obj: dict[str, Any], required: set[str], path: str) -> None:
    missing = sorted(required - set(obj))
    if missing:
        raise ValidationError(path, f"missing required field(s): {', '.join(missing)}")


def validate_evidence(items: Any) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    values = require_list(items, "$.evidence")
    if len(values) > MAX_EVIDENCE:
        raise ValidationError("$.evidence", f"must contain at most {MAX_EVIDENCE} items")
    result: list[dict[str, Any]] = []
    by_id: dict[str, dict[str, Any]] = {}
    allowed = {"id", "kind", "result", "reproducible", "fresh"}
    for index, raw in enumerate(values):
        path = f"$.evidence[{index}]"
        item = require_object(raw, path)
        reject_unknown(item, allowed, path)
        require_fields(item, allowed, path)
        evidence_id = require_string(item["id"], f"{path}.id")
        if evidence_id in by_id:
            raise ValidationError(f"{path}.id", f"duplicate evidence id {evidence_id!r}")
        normalized = {
            "id": evidence_id,
            "kind": require_string(item["kind"], f"{path}.kind", EVIDENCE_KINDS),
            "result": require_string(item["result"], f"{path}.result", EVIDENCE_RESULTS),
            "reproducible": require_bool(item["reproducible"], f"{path}.reproducible"),
            "fresh": require_bool(item["fresh"], f"{path}.fresh"),
        }
        by_id[evidence_id] = normalized
        result.append(normalized)
    return sorted(result, key=lambda item: item["id"]), by_id


def validate_evidence_ids(
    raw_ids: Any,
    path: str,
    evidence_by_id: dict[str, dict[str, Any]],
) -> list[str]:
    values = require_list(raw_ids, path)
    ids: list[str] = []
    for index, value in enumerate(values):
        evidence_id = require_string(value, f"{path}[{index}]")
        if evidence_id not in evidence_by_id:
            raise ValidationError(f"{path}[{index}]", f"unknown evidence id {evidence_id!r}")
        ids.append(evidence_id)
    if len(ids) != len(set(ids)):
        raise ValidationError(path, "must not contain duplicate evidence ids")
    return sorted(ids)


def has_reproducible_non_claim(ids: list[str], evidence: dict[str, dict[str, Any]]) -> bool:
    return any(evidence[item]["kind"] != "claim" and evidence[item]["reproducible"] for item in ids)


def has_reproducible_result(
    ids: list[str],
    evidence: dict[str, dict[str, Any]],
    kinds: set[str],
    results: set[str],
    require_fresh: bool = False,
) -> bool:
    return any(
        evidence[item]["kind"] in kinds
        and evidence[item]["result"] in results
        and evidence[item]["reproducible"]
        and (not require_fresh or evidence[item]["fresh"])
        for item in ids
    )


def validate_dimensions(
    items: Any,
    evidence_by_id: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    values = require_list(items, "$.dimensions")
    if not values or len(values) > MAX_DIMENSIONS:
        raise ValidationError("$.dimensions", f"must contain between 1 and {MAX_DIMENSIONS} items")
    allowed = {"id", "weight", "score", "verification", "evidence_ids"}
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    total_weight = 0
    for index, raw in enumerate(values):
        path = f"$.dimensions[{index}]"
        item = require_object(raw, path)
        reject_unknown(item, allowed, path)
        require_fields(item, allowed, path)
        dimension_id = require_string(item["id"], f"{path}.id")
        if dimension_id in seen:
            raise ValidationError(f"{path}.id", f"duplicate dimension id {dimension_id!r}")
        seen.add(dimension_id)
        weight = require_int(item["weight"], f"{path}.weight", 1, 100)
        score = require_int(item["score"], f"{path}.score", 0, 100)
        verification = require_string(
            item["verification"], f"{path}.verification", set(VERIFICATION_FACTORS)
        )
        evidence_ids = validate_evidence_ids(item["evidence_ids"], f"{path}.evidence_ids", evidence_by_id)
        if verification == "verified" and not has_reproducible_non_claim(evidence_ids, evidence_by_id):
            raise ValidationError(
                f"{path}.evidence_ids",
                "verified requires reproducible evidence whose kind is not claim",
            )
        if verification == "partial" and not evidence_ids:
            raise ValidationError(f"{path}.evidence_ids", "partial requires at least one evidence id")
        total_weight += weight
        result.append(
            {
                "id": dimension_id,
                "weight": weight,
                "score": score,
                "verification": verification,
                "evidence_ids": evidence_ids,
            }
        )
    if total_weight != 100:
        raise ValidationError("$.dimensions", f"weights must total 100; received {total_weight}")
    return sorted(result, key=lambda item: item["id"])


def validate_coverage(
    value: Any,
    evidence_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    coverage = require_object(value, "$.coverage")
    allowed = {"runtime", "selection", "cold_install", "required_references"}
    reject_unknown(coverage, allowed, "$.coverage")
    require_fields(coverage, allowed, "$.coverage")

    runtime = require_object(coverage["runtime"], "$.coverage.runtime")
    reject_unknown(runtime, {"level", "evidence_ids"}, "$.coverage.runtime")
    require_fields(runtime, {"level", "evidence_ids"}, "$.coverage.runtime")
    runtime_level = require_string(runtime["level"], "$.coverage.runtime.level", RUNTIME_LEVELS)
    runtime_ids = validate_evidence_ids(
        runtime["evidence_ids"], "$.coverage.runtime.evidence_ids", evidence_by_id
    )
    if runtime_level in {"full", "partial"} and not has_reproducible_result(
        runtime_ids,
        evidence_by_id,
        RUNTIME_EVIDENCE_KINDS,
        {"pass", "fail", "mixed"},
        require_fresh=True,
    ):
        raise ValidationError(
            "$.coverage.runtime.evidence_ids",
            f"{runtime_level} runtime coverage requires fresh, reproducible runtime, test, or trace evidence",
        )
    if runtime_level in {"static", "none"} and runtime_ids:
        raise ValidationError(
            "$.coverage.runtime.evidence_ids",
            f"must be empty when runtime level is {runtime_level!r}",
        )

    selection = require_object(coverage["selection"], "$.coverage.selection")
    reject_unknown(selection, {"level", "evidence_ids"}, "$.coverage.selection")
    require_fields(selection, {"level", "evidence_ids"}, "$.coverage.selection")
    selection_level = require_string(
        selection["level"], "$.coverage.selection.level", SELECTION_LEVELS
    )
    selection_ids = validate_evidence_ids(
        selection["evidence_ids"], "$.coverage.selection.evidence_ids", evidence_by_id
    )
    if selection_level in {"tested", "partial"} and not has_reproducible_result(
        selection_ids,
        evidence_by_id,
        SELECTION_EVIDENCE_KINDS,
        {"pass", "fail", "mixed"},
        require_fresh=True,
    ):
        raise ValidationError(
            "$.coverage.selection.evidence_ids",
            f"{selection_level} selection coverage requires fresh, reproducible test, log, or trace evidence",
        )
    if selection_level == "none" and selection_ids:
        raise ValidationError(
            "$.coverage.selection.evidence_ids", "must be empty when selection level is 'none'"
        )

    cold_install = require_object(coverage["cold_install"], "$.coverage.cold_install")
    reject_unknown(cold_install, {"level", "evidence_ids"}, "$.coverage.cold_install")
    require_fields(cold_install, {"level", "evidence_ids"}, "$.coverage.cold_install")
    install_level = require_string(
        cold_install["level"], "$.coverage.cold_install.level", INSTALL_LEVELS
    )
    install_ids = validate_evidence_ids(
        cold_install["evidence_ids"], "$.coverage.cold_install.evidence_ids", evidence_by_id
    )
    if install_level in {"tested", "partial"} and not has_reproducible_result(
        install_ids,
        evidence_by_id,
        INSTALL_EVIDENCE_KINDS,
        {"pass", "fail", "mixed"},
        require_fresh=True,
    ):
        raise ValidationError(
            "$.coverage.cold_install.evidence_ids",
            f"{install_level} cold-install coverage requires fresh, reproducible install, runtime, test, log, or trace evidence",
        )
    if install_level == "none" and install_ids:
        raise ValidationError(
            "$.coverage.cold_install.evidence_ids", "must be empty when cold-install level is 'none'"
        )

    references = require_object(
        coverage["required_references"], "$.coverage.required_references"
    )
    reference_allowed = {"total", "resolved", "evidence_ids"}
    reject_unknown(references, reference_allowed, "$.coverage.required_references")
    require_fields(references, reference_allowed, "$.coverage.required_references")
    total = require_int(references["total"], "$.coverage.required_references.total", 0, 10_000)
    resolved = require_int(references["resolved"], "$.coverage.required_references.resolved", 0, 10_000)
    if resolved > total:
        raise ValidationError(
            "$.coverage.required_references.resolved", f"must be <= total ({total}); received {resolved}"
        )
    reference_ids = validate_evidence_ids(
        references["evidence_ids"], "$.coverage.required_references.evidence_ids", evidence_by_id
    )
    if resolved and not has_reproducible_result(
        reference_ids,
        evidence_by_id,
        REFERENCE_EVIDENCE_KINDS,
        {"pass", "mixed"},
        require_fresh=True,
    ):
        raise ValidationError(
            "$.coverage.required_references.evidence_ids",
            "resolved references require fresh, reproducible reference, manifest, runtime, or test evidence",
        )
    return {
        "runtime": {"level": runtime_level, "evidence_ids": runtime_ids},
        "selection": {"level": selection_level, "evidence_ids": selection_ids},
        "cold_install": {"level": install_level, "evidence_ids": install_ids},
        "required_references": {
            "total": total,
            "resolved": resolved,
            "evidence_ids": reference_ids,
        },
    }


def validate_gates(
    items: Any,
    evidence_by_id: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    values = require_list(items, "$.gates")
    allowed = {"id", "state", "evidence_ids", "retest_evidence_ids"}
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, raw in enumerate(values):
        path = f"$.gates[{index}]"
        item = require_object(raw, path)
        reject_unknown(item, allowed, path)
        require_fields(item, allowed, path)
        gate_id = require_string(item["id"], f"{path}.id", set(SAFETY_GATES))
        if gate_id in seen:
            raise ValidationError(f"{path}.id", f"duplicate gate id {gate_id!r}")
        seen.add(gate_id)
        state = require_string(item["state"], f"{path}.state", {"active", "fixed"})
        evidence_ids = validate_evidence_ids(item["evidence_ids"], f"{path}.evidence_ids", evidence_by_id)
        retest_ids = validate_evidence_ids(
            item["retest_evidence_ids"], f"{path}.retest_evidence_ids", evidence_by_id
        )
        if state == "active" and not has_reproducible_result(
            evidence_ids,
            evidence_by_id,
            EVIDENCE_KINDS - {"claim"},
            {"fail", "mixed"},
        ):
            raise ValidationError(
                f"{path}.evidence_ids",
                "active gate requires reproducible fail or mixed evidence whose kind is not claim",
            )
        if state == "fixed" and not has_reproducible_result(
            retest_ids,
            evidence_by_id,
            RETEST_EVIDENCE_KINDS,
            {"pass"},
            require_fresh=True,
        ):
            raise ValidationError(
                f"{path}.retest_evidence_ids",
                "fixed gate requires fresh, reproducible passing retest evidence",
            )
        result.append(
            {
                "id": gate_id,
                "state": state,
                "evidence_ids": evidence_ids,
                "retest_evidence_ids": retest_ids,
            }
        )
    return sorted(result, key=lambda item: item["id"])


def validate_publish_checks(
    items: Any,
    evidence_by_id: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    values = require_list(items, "$.publish_checks")
    if not values:
        raise ValidationError("$.publish_checks", "must contain at least one explicit publish check")
    allowed = {"id", "required", "status", "evidence_ids"}
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, raw in enumerate(values):
        path = f"$.publish_checks[{index}]"
        item = require_object(raw, path)
        reject_unknown(item, allowed, path)
        require_fields(item, allowed, path)
        check_id = require_string(item["id"], f"{path}.id")
        if check_id in seen:
            raise ValidationError(f"{path}.id", f"duplicate publish check id {check_id!r}")
        seen.add(check_id)
        required = require_bool(item["required"], f"{path}.required")
        status = require_string(item["status"], f"{path}.status", {"pass", "fail", "unverified"})
        evidence_ids = validate_evidence_ids(item["evidence_ids"], f"{path}.evidence_ids", evidence_by_id)
        if status == "pass" and not has_reproducible_result(
            evidence_ids,
            evidence_by_id,
            EVIDENCE_KINDS - {"claim"},
            {"pass"},
            require_fresh=True,
        ):
            raise ValidationError(
                f"{path}.evidence_ids",
                "pass requires fresh, reproducible passing evidence whose kind is not claim",
            )
        if status == "fail" and not has_reproducible_result(
            evidence_ids, evidence_by_id, EVIDENCE_KINDS - {"claim"}, {"fail", "mixed"}
        ):
            raise ValidationError(
                f"{path}.evidence_ids", "fail requires reproducible fail or mixed evidence"
            )
        result.append(
            {"id": check_id, "required": required, "status": status, "evidence_ids": evidence_ids}
        )
    return sorted(result, key=lambda item: item["id"])


def validate_target_publish_checks(
    publish_target: str,
    checks: list[dict[str, Any]],
    evidence_by_id: dict[str, dict[str, Any]],
) -> list[str]:
    required_specs = TARGET_REQUIRED_CHECKS[publish_target]
    checks_by_id = {item["id"]: item for item in checks}
    missing = sorted(set(required_specs) - set(checks_by_id))
    if missing:
        raise ValidationError(
            "$.publish_checks",
            f"{publish_target!r} requires publish check(s): {', '.join(missing)}",
        )
    for check_id in sorted(required_specs):
        check = checks_by_id[check_id]
        if not check["required"]:
            raise ValidationError(
                "$.publish_checks",
                f"target-required publish check {check_id!r} must set required to true",
            )
        if check["status"] == "pass" and not has_reproducible_result(
            check["evidence_ids"],
            evidence_by_id,
            required_specs[check_id],
            {"pass"},
            require_fresh=True,
        ):
            raise ValidationError(
                "$.publish_checks",
                f"passing target-required check {check_id!r} requires fresh, reproducible evidence of an allowed kind: {', '.join(sorted(required_specs[check_id]))}",
            )
    return sorted(required_specs)


def validate(payload: Any) -> dict[str, Any]:
    root = require_object(payload, "$")
    required = {
        "schema_version",
        "mode",
        "rubric_id",
        "publish_target",
        "dimensions",
        "evidence",
        "coverage",
        "gates",
        "publish_checks",
    }
    reject_unknown(root, required, "$")
    require_fields(root, required, "$")
    schema_version = require_string(root["schema_version"], "$.schema_version")
    if schema_version != SCHEMA_VERSION:
        raise ValidationError(
            "$.schema_version", f"must equal {SCHEMA_VERSION!r}; received {schema_version!r}"
        )
    mode = require_string(root["mode"], "$.mode", MODES)
    rubric_id = require_string(root["rubric_id"], "$.rubric_id")
    publish_target = require_string(
        root["publish_target"], "$.publish_target", set(PUBLISH_THRESHOLDS)
    )
    evidence, evidence_by_id = validate_evidence(root["evidence"])
    dimensions = validate_dimensions(root["dimensions"], evidence_by_id)
    coverage = validate_coverage(root["coverage"], evidence_by_id)
    gates = validate_gates(root["gates"], evidence_by_id)
    publish_checks = validate_publish_checks(root["publish_checks"], evidence_by_id)
    target_required_check_ids = validate_target_publish_checks(
        publish_target, publish_checks, evidence_by_id
    )
    return {
        "schema_version": schema_version,
        "mode": mode,
        "rubric_id": rubric_id,
        "publish_target": publish_target,
        "dimensions": dimensions,
        "evidence": evidence,
        "coverage": coverage,
        "gates": gates,
        "publish_checks": publish_checks,
        "target_required_check_ids": target_required_check_ids,
    }


def quantize(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def as_json_number(value: Decimal) -> int | float:
    value = quantize(value)
    if value == value.to_integral_value():
        return int(value)
    return float(value)


def worse_confidence(first: str, second: str) -> str:
    return first if CONFIDENCE_ORDER[first] >= CONFIDENCE_ORDER[second] else second


def confidence_for(
    evidence_percent: Decimal,
    reference_percent: Decimal,
    runtime_level: str,
    selection_level: str,
    install_level: str,
) -> str:
    if evidence_percent >= 85 and reference_percent >= 90:
        base = "A"
    elif evidence_percent >= 65 and reference_percent >= 70:
        base = "B"
    elif evidence_percent >= 40:
        base = "C"
    else:
        base = "D"
    confidence = worse_confidence(base, RUNTIME_CONFIDENCE_CAP[runtime_level])
    confidence = worse_confidence(confidence, SELECTION_CONFIDENCE_CAP[selection_level])
    return worse_confidence(confidence, INSTALL_CONFIDENCE_CAP[install_level])


def compute(data: dict[str, Any]) -> dict[str, Any]:
    dimensions_output: list[dict[str, Any]] = []
    raw_score = Decimal("0")
    evidence_percent = Decimal("0")
    for dimension in data["dimensions"]:
        score = Decimal(dimension["score"])
        weight = Decimal(dimension["weight"])
        contribution = score * weight / Decimal("100")
        raw_score += contribution
        evidence_percent += weight * VERIFICATION_FACTORS[dimension["verification"]]
        dimensions_output.append(
            {
                "contribution": as_json_number(contribution),
                "id": dimension["id"],
                "score": dimension["score"],
                "verification": dimension["verification"],
                "weight": dimension["weight"],
            }
        )

    references = data["coverage"]["required_references"]
    reference_percent = (
        Decimal(references["resolved"]) * Decimal("100") / Decimal(references["total"])
        if references["total"]
        else Decimal("100")
    )
    runtime_level = data["coverage"]["runtime"]["level"]
    selection_level = data["coverage"]["selection"]["level"]
    install_level = data["coverage"]["cold_install"]["level"]
    confidence = confidence_for(
        evidence_percent, reference_percent, runtime_level, selection_level, install_level
    )
    applied_caps: list[dict[str, Any]] = [
        {
            "id": f"confidence-{confidence.lower()}",
            "source": "evidence-confidence",
            "value": as_json_number(CONFIDENCE_SCORE_CAP[confidence]),
        }
    ]

    distribution_evidence_gaps: list[str] = []
    if data["publish_target"] == "team-shared":
        if runtime_level in {"static", "none"}:
            distribution_evidence_gaps.append("runtime")
            applied_caps.append(
                {
                    "id": "team-runtime-evidence",
                    "source": "distribution-evidence",
                    "value": as_json_number(TEAM_EVIDENCE_CAP),
                }
            )
        if selection_level in {"claimed", "none"}:
            distribution_evidence_gaps.append("selection")
            applied_caps.append(
                {
                    "id": "team-selection-evidence",
                    "source": "distribution-evidence",
                    "value": as_json_number(TEAM_EVIDENCE_CAP),
                }
            )
    if data["publish_target"] in {"public-marketplace", "privileged-production", "high-stakes"}:
        if runtime_level in {"static", "none"}:
            distribution_evidence_gaps.append("runtime")
            applied_caps.append(
                {
                    "id": "public-runtime-evidence",
                    "source": "marketplace-evidence",
                    "value": as_json_number(PUBLIC_EVIDENCE_CAP),
                }
            )
        if selection_level in {"claimed", "none"}:
            distribution_evidence_gaps.append("selection")
            applied_caps.append(
                {
                    "id": "public-selection-evidence",
                    "source": "marketplace-evidence",
                    "value": as_json_number(PUBLIC_EVIDENCE_CAP),
                }
            )
        if install_level in {"claimed", "none"}:
            distribution_evidence_gaps.append("cold-install")
            applied_caps.append(
                {
                    "id": "public-cold-install-evidence",
                    "source": "marketplace-evidence",
                    "value": as_json_number(PUBLIC_EVIDENCE_CAP),
                }
            )
        if references["resolved"] < references["total"]:
            distribution_evidence_gaps.append("required-references")
            applied_caps.append(
                {
                    "id": "public-required-references",
                    "source": "marketplace-evidence",
                    "value": as_json_number(PUBLIC_EVIDENCE_CAP),
                }
            )

    active_gates: list[dict[str, Any]] = []
    for gate in data["gates"]:
        if gate["state"] == "active":
            cap = SAFETY_GATES[gate["id"]]
            active_gates.append({"cap": as_json_number(cap), "id": gate["id"]})
            applied_caps.append(
                {"id": gate["id"], "source": "safety-gate", "value": as_json_number(cap)}
            )

    readiness_score = min([raw_score] + [Decimal(str(item["value"])) for item in applied_caps])
    threshold = PUBLISH_THRESHOLDS[data["publish_target"]]
    required_failed = [
        item["id"] for item in data["publish_checks"] if item["required"] and item["status"] == "fail"
    ]
    required_unverified = [
        item["id"]
        for item in data["publish_checks"]
        if item["required"] and item["status"] == "unverified"
    ]
    optional_gaps = [
        item["id"]
        for item in data["publish_checks"]
        if not item["required"] and item["status"] != "pass"
    ]

    if active_gates:
        decision = "BLOCKED"
    elif required_failed:
        decision = "NOT_READY"
    elif required_unverified or distribution_evidence_gaps:
        decision = "INSUFFICIENT_EVIDENCE"
    elif readiness_score < threshold:
        decision = "NOT_READY"
    elif optional_gaps:
        decision = "READY_WITH_CONDITIONS"
    else:
        decision = "READY"

    fingerprint_payload = {
        "dimensions": [{"id": item["id"], "weight": item["weight"]} for item in data["dimensions"]],
        "mode": data["mode"],
        "publish_target": data["publish_target"],
        "rubric_id": data["rubric_id"],
    }
    fingerprint_bytes = json.dumps(
        fingerprint_payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")
    fingerprint = "sha256:" + hashlib.sha256(fingerprint_bytes).hexdigest()

    return {
        "active_gates": active_gates,
        "applied_caps": sorted(applied_caps, key=lambda item: (item["value"], item["id"])),
        "coverage": {
            "confidence": confidence,
            "cold_install": install_level,
            "evidence_percent": as_json_number(evidence_percent),
            "reference_percent": as_json_number(reference_percent),
            "runtime": runtime_level,
            "selection": selection_level,
        },
        "decision": decision,
        "dimensions": dimensions_output,
        "distribution_evidence_gaps": distribution_evidence_gaps,
        "mode": data["mode"],
        "ok": True,
        "policy_version": POLICY_VERSION,
        "publish_checks": {
            "failed_required": required_failed,
            "optional_gaps": optional_gaps,
            "target_required": data["target_required_check_ids"],
            "unverified_required": required_unverified,
        },
        "publish_target": data["publish_target"],
        "publish_threshold": as_json_number(threshold),
        "rubric_fingerprint": fingerprint,
        "rubric_id": data["rubric_id"],
        "schema_version": SCHEMA_VERSION,
        "scores": {
            "raw_quality": as_json_number(raw_score),
            "publish_readiness": as_json_number(readiness_score),
        },
        "vetoed": bool(active_gates),
    }


def render(result: dict[str, Any], pretty: bool) -> str:
    if pretty:
        return json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"
    return json.dumps(
        result,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
        allow_nan=False,
    ) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = JsonArgumentParser(description=__doc__)
    parser.add_argument("--pretty", action="store_true", help="pretty-print deterministic JSON")
    parser.add_argument("input", type=Path, help="path to a scorecard JSON file")
    args = parser.parse_args(argv)
    try:
        result = compute(validate(load_payload(args.input)))
    except ValidationError as exc:
        emit_error("validation_error", exc.path, exc.message)
        return 1
    sys.stdout.write(render(result, args.pretty))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
