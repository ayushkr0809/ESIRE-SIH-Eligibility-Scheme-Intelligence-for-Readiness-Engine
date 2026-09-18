from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.db import mongo, neo4j_db
from app.models import SchemeRecord

SEED_PATH = Path(__file__).resolve().parent.parent / "data" / "seed_schemes.json"


def load_seed_schemes() -> list[dict[str, Any]]:
    return json.loads(SEED_PATH.read_text(encoding="utf-8"))


def seed_catalog(db: Session) -> None:
    schemes = load_seed_schemes()
    for scheme in schemes:
        mongo.upsert("schemes", scheme["id"], scheme)
        record = db.get(SchemeRecord, scheme["id"])
        if record is None:
            record = SchemeRecord(
                id=scheme["id"],
                code=scheme.get("code") or scheme["id"],
                name=scheme["name"],
                department=scheme.get("department") or "",
                source=scheme.get("source") or "prototype_seed",
                is_seed=True,
            )
            db.add(record)
        else:
            record.name = scheme["name"]
            record.department = scheme.get("department") or ""
        _graph_scheme(scheme)
    db.commit()


def _graph_scheme(scheme: dict[str, Any]) -> None:
    neo4j_db.merge_node("Scheme", scheme["id"], {"name": scheme["name"], "code": scheme.get("code")})
    for category in scheme.get("categories") or []:
        neo4j_db.merge_node("Category", category, {"name": category})
        neo4j_db.merge_rel("Scheme", scheme["id"], "BELONGS_TO", "Category", category)
    for group in scheme.get("target_groups") or []:
        neo4j_db.merge_node("Group", group, {"name": group})
        neo4j_db.merge_rel("Scheme", scheme["id"], "TARGETS_GROUP", "Group", group)
    for location in scheme.get("locations") or []:
        neo4j_db.merge_node("Location", location, {"name": location})
        neo4j_db.merge_rel("Scheme", scheme["id"], "AVAILABLE_IN", "Location", location)
    for benefit in scheme.get("benefits") or []:
        neo4j_db.merge_node("Benefit", benefit, {"name": benefit})
        neo4j_db.merge_rel("Scheme", scheme["id"], "PROVIDES", "Benefit", benefit)
    for spec in scheme.get("constraints") or []:
        neo4j_db.merge_node("Criterion", spec["id"], {"explanation": spec.get("explanation")})
        neo4j_db.merge_rel("Criterion", spec["id"], "APPLIES_TO", "Scheme", scheme["id"])
    for document in scheme.get("documents") or []:
        neo4j_db.merge_node("DocumentType", document["id"], {"name": document.get("name")})
        neo4j_db.merge_rel("Scheme", scheme["id"], "REQUIRES_DOCUMENT", "DocumentType", document["id"])
        for proves in document.get("proves") or []:
            neo4j_db.merge_node("Criterion", proves, {"name": proves})
            neo4j_db.merge_rel("DocumentType", document["id"], "PROVES", "Criterion", proves)


def all_schemes() -> list[dict[str, Any]]:
    stored = mongo.find_all("schemes")
    if stored:
        cleaned = []
        for item in stored:
            row = dict(item)
            row.pop("_id", None)
            cleaned.append(row)
        return cleaned
    return load_seed_schemes()


def get_scheme(scheme_id: str) -> dict[str, Any] | None:
    row = mongo.find_one("schemes", scheme_id)
    if row:
        row = dict(row)
        row.pop("_id", None)
        return row
    for item in load_seed_schemes():
        if item["id"] == str(scheme_id):
            return item
    return None


def upsert_scheme(db: Session, scheme: dict[str, Any]) -> dict[str, Any]:
    mongo.upsert("schemes", scheme["id"], scheme)
    record = db.get(SchemeRecord, scheme["id"])
    if record is None:
        db.add(
            SchemeRecord(
                id=scheme["id"],
                code=scheme.get("code") or scheme["id"],
                name=scheme["name"],
                department=scheme.get("department") or "",
                source=scheme.get("source") or "admin",
                is_seed=False,
            )
        )
    else:
        record.name = scheme["name"]
        record.department = scheme.get("department") or ""
        record.source = scheme.get("source") or record.source
    _graph_scheme(scheme)
    db.commit()
    return scheme
