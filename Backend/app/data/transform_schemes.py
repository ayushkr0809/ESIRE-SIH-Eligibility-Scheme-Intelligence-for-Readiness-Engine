"""
One-off transform: converts app/data/raw_schemes_source.json (the flat
government-scheme dataset) into app/data/seed_schemes.json — the schema
the rest of the backend (z3_engine, scoring, catalog, matching) expects:
constraints[] with {id,type,field/min/max/value,required,weight,explanation},
documents[] with {id,name,weight,mandatory_for_eligibility,proves},
target_groups[]/locations[] normalized into tokens that line up with what
Neo4j-based candidate matching (app/db/neo4j_db.related_scheme_ids) derives
from a user's profile, so the graph layer actually clusters related schemes
instead of just storing disconnected nodes.

Run manually whenever raw_schemes_source.json changes:
    python3 app/data/transform_schemes.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "raw_schemes_source.json"
OUT = HERE / "seed_schemes.json"

# Canonical group tokens a user's profile can produce (see
# app/db/neo4j_db.related_scheme_ids): occupation_type value, category value,
# "woman" (if gender == female), "entrepreneur" (if is_entrepreneur), "citizen".
# We scan each scheme's free-text target_groups/keywords/business_types for
# hints of these same tokens so the graph edges actually mean something.
GROUP_KEYWORDS = {
    "farmer": ["farmer", "agricultur", "agri "],
    "entrepreneur": ["entrepreneur", "startup", "start-up", "business owner"],
    "self_employed": ["self-employed", "self employed"],
    "student": ["student", "school", "college", "scholar"],
    "unemployed": ["unemployed", "job seeker", "jobseeker"],
    "small_business": ["small business", "small enterprise", "msme", "micro and small"],
    "micro_enterprise": ["micro entrepreneur", "micro enterprise", "micro food"],
    "salaried": ["salaried", "worker", "employee", "employer"],
    "artisan": ["artisan", "craft", "weaver", "handloom", "handicraft", "coir"],
    "street_vendor": ["street vendor", "vending", "vendor"],
    "woman": ["women", "woman", "mahila", "female"],
    "youth": ["youth"],
    "elderly": ["elderly", "widow", "senior"],
}

SOCIAL_CATEGORY_MAP = {
    "sc": "sc",
    "st": "st",
    "obc": "obc",
    "pwd": "pwd",
    "minority": "minority",
}

DOC_WEIGHT = 10


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", text.strip().lower()).strip("_")
    return slug or "document"


def derive_groups(entry: dict) -> list[str]:
    haystack = " ".join(
        entry.get("target_groups", [])
        + entry.get("keywords", [])
        + entry.get("business_types", [])
    ).lower()

    tokens: list[str] = []
    for token, hints in GROUP_KEYWORDS.items():
        if any(hint in haystack for hint in hints):
            tokens.append(token)

    for cat in entry.get("social_categories") or []:
        mapped = SOCIAL_CATEGORY_MAP.get(cat.strip().lower())
        if mapped and mapped not in tokens:
            tokens.append(mapped)

    if entry.get("gender") == "FEMALE" and "woman" not in tokens:
        tokens.append("woman")

    tokens.append("citizen")  # every scheme is at least a candidate for any citizen
    return list(dict.fromkeys(tokens))


def derive_locations(entry: dict) -> list[str]:
    states = entry.get("states") or ["ALL"]
    if states == ["ALL"]:
        return ["India"]
    # Keep the specific state(s) AND "India" so the scheme still surfaces as a
    # general candidate while being prioritized for the matching state profile.
    return list(dict.fromkeys([*states, "India"]))


def build_constraints(entry: dict) -> list[dict]:
    constraints: list[dict] = []

    constraints.append(
        {
            "id": "citizenship",
            "type": "equals",
            "field": "citizenship",
            "value": "IN",
            "required": True,
            "weight": 10,
            "explanation": "Applicant should be an Indian citizen",
        }
    )

    age_min = entry.get("age_min")
    age_max = entry.get("age_max")
    if age_min is not None or age_max is not None:
        constraints.append(
            {
                "id": "age_range",
                "type": "age_range",
                "min": age_min if age_min is not None else 0,
                "max": age_max if age_max is not None else 120,
                "required": True,
                "weight": 20,
                "explanation": f"Applicant should be between {age_min or 0} and {age_max or 120} years old",
            }
        )

    income_max = entry.get("income_max")
    if income_max is not None:
        constraints.append(
            {
                "id": "income_limit",
                "type": "max_number",
                "field": "annual_income",
                "value": income_max,
                "required": True,
                "weight": 25,
                "explanation": f"Annual income should not exceed \u20b9{income_max:,}",
            }
        )

    gender = entry.get("gender")
    if gender and gender != "ALL":
        constraints.append(
            {
                "id": "gender",
                "type": "in_set",
                "field": "gender",
                "values": [gender.lower()],
                "required": True,
                "weight": 15,
                "explanation": f"Open to {gender.title()} applicants",
            }
        )

    social_categories = entry.get("social_categories") or []
    specific_categories = [c for c in social_categories if c.upper() != "ALL"]
    if specific_categories:
        constraints.append(
            {
                "id": "social_category",
                "type": "in_set",
                "field": "category",
                "values": [c.lower() for c in specific_categories],
                "required": True,
                "weight": 20,
                "explanation": f"Reserved for {', '.join(specific_categories)} category applicants",
            }
        )

    states = entry.get("states") or ["ALL"]
    if states != ["ALL"]:
        constraints.append(
            {
                "id": "state",
                "type": "in_set",
                "field": "state",
                "values": [s.lower() for s in states],
                "required": True,
                "weight": 10,
                "explanation": f"Available to residents of {', '.join(states)}",
            }
        )

    return constraints


def build_documents(entry: dict) -> list[dict]:
    documents = []
    seen_ids = set()
    for raw_name in entry.get("documents") or []:
        doc_id = slugify(raw_name)
        if doc_id in seen_ids:
            continue
        seen_ids.add(doc_id)
        documents.append(
            {
                "id": doc_id,
                "name": raw_name,
                "weight": DOC_WEIGHT,
                "mandatory_for_eligibility": False,
                "proves": [],
            }
        )
    return documents


def build_scheme(entry: dict) -> dict:
    benefit = entry.get("benefit") or ""
    target_groups_text = ", ".join(entry.get("target_groups") or [])
    business_types_text = ", ".join(entry.get("business_types") or [])
    full_description = benefit
    if target_groups_text:
        full_description += f" Primarily aimed at: {target_groups_text}."
    if business_types_text:
        full_description += f" Relevant business/work types: {business_types_text}."

    return {
        "id": entry["id"],
        "code": entry["id"],
        "name": entry["name"],
        "department": entry.get("ministry") or "",
        "source": "data_gov_seed",
        "source_note": "Prototype seed data compiled for demonstration. Verify current details on the official scheme portal before advising an applicant.",
        "description": benefit,
        "full_description": full_description,
        "deadline": "Open all year",
        "categories": [entry.get("category")] if entry.get("category") else [],
        "target_groups": derive_groups(entry),
        "locations": derive_locations(entry),
        "benefits": [benefit] if benefit else [],
        "constraints": build_constraints(entry),
        "documents": build_documents(entry),
    }


def main() -> None:
    raw = json.loads(SOURCE.read_text(encoding="utf-8"))
    transformed = [build_scheme(entry) for entry in raw]
    OUT.write_text(json.dumps(transformed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(transformed)} schemes to {OUT}")


if __name__ == "__main__":
    main()
