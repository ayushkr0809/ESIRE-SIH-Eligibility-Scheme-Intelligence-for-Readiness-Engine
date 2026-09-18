from __future__ import annotations

from typing import Any

from app.config import get_settings
from app.services.z3_engine import VerificationResult

settings = get_settings()

READY_STATUSES = {"uploaded", "extracted", "verified"}


def _round_score(value: float) -> float:
    return round(max(0.0, min(100.0, value)), 2)


def eligibility_score(scheme: dict[str, Any], verification: VerificationResult) -> float:
    constraints = scheme.get("constraints") or []
    total = sum(int(item.get("weight") or 0) for item in constraints)
    if total <= 0:
        return 100.0
    status_by_id = {item.constraint_id: item.status for item in verification.outcomes}
    earned = 0
    for spec in constraints:
        weight = int(spec.get("weight") or 0)
        status = status_by_id.get(spec["id"])
        if status == "sat":
            earned += weight
        elif status == "unknown":
            earned += weight * 0.25
    return _round_score(100.0 * earned / total)


def document_score(scheme: dict[str, Any], submitted: dict[str, str]) -> tuple[float, list[str], list[str], list[dict[str, Any]]]:
    required = scheme.get("documents") or []
    if not required:
        return 100.0, [], [], []
    total = sum(int(item.get("weight") or 0) for item in required) or 1
    earned = 0
    missing = []
    present = []
    details = []
    for item in required:
        doc_id = item["id"]
        weight = int(item.get("weight") or 0)
        status = submitted.get(doc_id)
        contributed = weight if status in READY_STATUSES else 0
        earned += contributed
        row = {
            "id": doc_id,
            "name": item.get("name") or doc_id,
            "weight": weight,
            "status": status or "missing",
            "proves": item.get("proves") or [],
            "mandatory_for_eligibility": bool(item.get("mandatory_for_eligibility")),
        }
        details.append(row)
        if status in READY_STATUSES:
            present.append(item.get("name") or doc_id)
        else:
            missing.append(item.get("name") or doc_id)
    return _round_score(100.0 * earned / total), present, missing, details


def mandatory_docs_unknown(scheme: dict[str, Any], submitted: dict[str, str]) -> list[str]:
    missing = []
    for item in scheme.get("documents") or []:
        if item.get("mandatory_for_eligibility") and submitted.get(item["id"]) not in READY_STATUSES:
            missing.append(item.get("name") or item["id"])
    return missing


def combine_scores(eligibility: float, documents: float) -> float:
    total_weight = settings.eligibility_weight + settings.document_weight
    if total_weight <= 0:
        return 0.0
    value = (
        settings.eligibility_weight * eligibility + settings.document_weight * documents
    ) / total_weight
    return _round_score(value)


def display_band(final_score: float) -> str | None:
    if final_score <= settings.display_threshold:
        return None
    if final_score > 75:
        return "strong"
    return "moderate"
