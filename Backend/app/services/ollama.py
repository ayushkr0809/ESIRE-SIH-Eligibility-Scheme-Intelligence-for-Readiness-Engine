from __future__ import annotations

import json
import re
from typing import Any

import httpx

from app.config import get_settings

settings = get_settings()

EXTRACT_SCHEMA = {
    "name": None,
    "age": None,
    "gender": None,
    "state": None,
    "district": None,
    "occupation": None,
    "occupation_type": None,
    "annual_income": None,
    "category": None,
    "is_entrepreneur": None,
    "has_existing_business": None,
    "has_land": None,
    "citizenship": "IN",
    "needs": [],
    "summary": "",
}

ALLOWED_OCCUPATION = {
    "farmer",
    "entrepreneur",
    "self_employed",
    "student",
    "salaried",
    "unemployed",
    "small_business",
    "micro_enterprise",
}
ALLOWED_CATEGORY = {"general", "sc", "st", "obc", "ews"}
ALLOWED_GENDER = {"female", "male", "other"}


def _extract_json_blob(text: str) -> dict[str, Any] | None:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def validate_extraction(data: dict[str, Any]) -> dict[str, Any]:
    out = dict(EXTRACT_SCHEMA)
    if not isinstance(data, dict):
        return out
    if isinstance(data.get("name"), str):
        out["name"] = data["name"].strip()[:200] or None
    age = data.get("age")
    if isinstance(age, int) and 0 < age < 120:
        out["age"] = age
    elif isinstance(age, str) and age.isdigit():
        value = int(age)
        if 0 < value < 120:
            out["age"] = value
    gender = str(data.get("gender") or "").lower()
    out["gender"] = gender if gender in ALLOWED_GENDER else None
    for field in ("state", "district", "occupation"):
        value = data.get(field)
        if isinstance(value, str) and value.strip():
            out[field] = value.strip()[:120]
    occ = str(data.get("occupation_type") or "").lower().replace(" ", "_")
    out["occupation_type"] = occ if occ in ALLOWED_OCCUPATION else None
    income = data.get("annual_income")
    if isinstance(income, (int, float)) and income >= 0:
        out["annual_income"] = int(income)
    cat = str(data.get("category") or "").lower()
    out["category"] = cat if cat in ALLOWED_CATEGORY else None
    for flag in ("is_entrepreneur", "has_existing_business", "has_land"):
        if isinstance(data.get(flag), bool):
            out[flag] = data[flag]
    cit = str(data.get("citizenship") or "IN").upper()
    out["citizenship"] = "IN" if cit in {"IN", "INDIA", "INDIAN"} else None
    needs = data.get("needs")
    if isinstance(needs, list):
        out["needs"] = [str(item)[:80] for item in needs[:12]]
    if isinstance(data.get("summary"), str):
        out["summary"] = data["summary"][:500]
    return out


class OllamaService:
    def __init__(self) -> None:
        self.available = False
        self.last_error: str | None = None

    def ping(self) -> bool:
        try:
            response = httpx.get(f"{settings.ollama_base_url}/api/tags", timeout=2.0)
            self.available = response.status_code == 200
            return self.available
        except Exception as exc:
            self.available = False
            self.last_error = str(exc)
            return False

    def generate_json(self, prompt: str, language: str = "en") -> dict[str, Any] | None:
        try:
            response = httpx.post(
                f"{settings.ollama_base_url}/api/generate",
                json={
                    "model": settings.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                    "options": {"temperature": 0.1},
                },
                timeout=settings.ollama_timeout_seconds,
            )
            response.raise_for_status()
            body = response.json()
            parsed = _extract_json_blob(body.get("response") or "")
            self.available = True
            return parsed
        except Exception as exc:
            self.available = False
            self.last_error = str(exc)
            return None

    def extract_profile(self, text: str, language: str = "en") -> dict[str, Any] | None:
        prompt = (
            f"You extract structured citizen profile fields from multilingual text. "
            f"Respond only with JSON. User language code: {language}.\n"
            f"Schema keys: {list(EXTRACT_SCHEMA)}. occupation_type one of {sorted(ALLOWED_OCCUPATION)}. "
            f"category one of {sorted(ALLOWED_CATEGORY)}. gender one of {sorted(ALLOWED_GENDER)}. "
            f"citizenship is IN if the person is Indian.\n"
            f"Text:\n{text}"
        )
        parsed = self.generate_json(prompt, language)
        return validate_extraction(parsed) if parsed else None

    def explain_match(self, payload: dict[str, Any], language: str = "en") -> str | None:
        prompt = (
            f"Write a short citizen-friendly explanation in language {language}. "
            f"Do not mention Z3 or SAT. JSON context:\n{json.dumps(payload)[:2500]}"
        )
        parsed = self.generate_json(
            prompt + ' Return JSON {"explanation": "..."}',
            language,
        )
        if parsed and isinstance(parsed.get("explanation"), str):
            return parsed["explanation"][:600]
        return None


ollama_service = OllamaService()
