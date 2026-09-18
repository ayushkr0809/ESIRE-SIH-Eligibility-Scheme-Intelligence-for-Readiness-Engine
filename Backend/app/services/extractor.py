from __future__ import annotations

import re
from typing import Any

from app.services.ollama import ALLOWED_OCCUPATION, ollama_service, validate_extraction

STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa",
    "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala",
    "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland",
    "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
    "Uttar Pradesh", "Uttarakhand", "West Bengal", "Delhi", "Jammu and Kashmir",
    "Ladakh", "Puducherry", "Jaipur",
]

STATE_ALIASES = {"jaipur": "Rajasthan"}


def heuristic_extract(text: str) -> dict[str, Any]:
    lowered = text.lower()
    data: dict[str, Any] = {"citizenship": "IN", "summary": text[:400]}

    age_match = re.search(r"\b(\d{1,2})\s*(years?|yrs?|saal)\b", lowered)
    if not age_match:
        age_match = re.search(r"\bi am\s+(\d{1,2})\b", lowered)
    if age_match:
        data["age"] = int(age_match.group(1))

    if re.search(r"\b(woman|female|girl|mahila|stree)\b", lowered):
        data["gender"] = "female"
    elif re.search(r"\b(man|male|boy)\b", lowered):
        data["gender"] = "male"

    for state in STATES:
        if state.lower() in lowered:
            data["state"] = STATE_ALIASES.get(state.lower(), state if state != "Jaipur" else "Rajasthan")
            break

    income_match = re.search(r"(?:rs\.?|₹|inr)?\s*(\d[\d,]*)\s*(lakh|lakhs)?", lowered)
    if income_match:
        amount = int(income_match.group(1).replace(",", ""))
        if income_match.group(2):
            amount *= 100000
        if amount > 1000:
            data["annual_income"] = amount

    if re.search(r"\b(farmer|kisan|farming|agriculture)\b", lowered):
        data["occupation_type"] = "farmer"
        data["occupation"] = "farmer"
        data["has_land"] = True
    elif re.search(r"\b(tailor|shop|business|enterprise|udyam|entrepreneur|self[- ]employed)\b", lowered):
        data["occupation_type"] = "entrepreneur"
        data["occupation"] = "small business"
        data["is_entrepreneur"] = True
        data["has_existing_business"] = "start" not in lowered and "planning" not in lowered
    elif re.search(r"\bstudent\b", lowered):
        data["occupation_type"] = "student"
    elif re.search(r"\bsalaried|job|employee\b", lowered):
        data["occupation_type"] = "salaried"

    if "sc/st" in lowered or re.search(r"\bscheduled caste\b", lowered):
        data["category"] = "sc"
    elif re.search(r"\bst\b|scheduled tribe", lowered):
        data["category"] = "st"
    elif re.search(r"\bobc\b", lowered):
        data["category"] = "obc"

    if "land" in lowered:
        data["has_land"] = True
    if data.get("occupation_type") in ALLOWED_OCCUPATION and data["occupation_type"] != "farmer":
        data["is_entrepreneur"] = data.get("is_entrepreneur", data["occupation_type"] in {"entrepreneur", "self_employed", "micro_enterprise", "small_business"})

    if "loan" in lowered or "expand" in lowered:
        data["needs"] = ["credit"]
    return validate_extraction(data)


def extract_profile(text: str, language: str = "en") -> tuple[dict[str, Any], str]:
    heuristic = heuristic_extract(text)
    ai = ollama_service.extract_profile(text, language=language)
    if not ai:
        return heuristic, "heuristic"
    merged = dict(heuristic)
    for key, value in ai.items():
        if value not in (None, "", []):
            merged[key] = value
    return validate_extraction(merged), "ollama+heuristic"
