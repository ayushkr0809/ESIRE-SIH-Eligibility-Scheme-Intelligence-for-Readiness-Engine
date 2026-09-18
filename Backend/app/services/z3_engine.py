from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from z3 import And, Bool, BoolVal, Int, Or, Solver, sat


@dataclass
class ConstraintOutcome:
    constraint_id: str
    explanation: str
    status: str
    weight: int


@dataclass
class VerificationResult:
    status: str
    outcomes: list[ConstraintOutcome] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    uncertain: list[str] = field(default_factory=list)
    satisfied: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "failed_conditions": self.failed,
            "uncertain_conditions": self.uncertain,
            "satisfied_conditions": self.satisfied,
            "outcomes": [outcome.__dict__ for outcome in self.outcomes],
        }


def _get(profile: dict[str, Any], field: str) -> Any:
    return profile.get(field)


def _known(value: Any) -> bool:
    return value is not None and value != ""


def _eval_simple(profile: dict[str, Any], spec: dict[str, Any]) -> str:
    ctype = spec["type"]
    if ctype == "age_range":
        age = _get(profile, "age")
        if not _known(age):
            return "unknown"
        solver = Solver()
        age_var = Int("age")
        solver.add(age_var == int(age))
        solver.add(age_var >= int(spec.get("min", 0)))
        solver.add(age_var <= int(spec.get("max", 120)))
        return "sat" if solver.check() == sat else "unsat"
    if ctype == "max_number":
        value = _get(profile, spec["field"])
        if not _known(value):
            return "unknown"
        solver = Solver()
        number = Int("n")
        solver.add(number == int(value))
        solver.add(number <= int(spec["value"]))
        return "sat" if solver.check() == sat else "unsat"
    if ctype == "min_number":
        value = _get(profile, spec["field"])
        if not _known(value):
            return "unknown"
        solver = Solver()
        number = Int("n")
        solver.add(number == int(value))
        solver.add(number >= int(spec["value"]))
        return "sat" if solver.check() == sat else "unsat"
    if ctype == "equals":
        value = _get(profile, spec["field"])
        if not _known(value):
            return "unknown"
        solver = Solver()
        flag = Bool("eq")
        solver.add(flag == BoolVal(value == spec["value"]))
        solver.add(flag)
        return "sat" if solver.check() == sat else "unsat"
    if ctype == "in_set":
        value = _get(profile, spec["field"])
        if not _known(value):
            return "unknown"
        values = [str(item).lower() if isinstance(item, str) else item for item in spec.get("values", [])]
        actual = value.lower() if isinstance(value, str) else value
        solver = Solver()
        flag = Bool("inset")
        solver.add(flag == BoolVal(actual in values))
        solver.add(flag)
        return "sat" if solver.check() == sat else "unsat"
    if ctype == "any_of":
        results = [_eval_simple(profile, clause) for clause in spec.get("clauses", [])]
        if "sat" in results:
            return "sat"
        if all(item == "unsat" for item in results) and results:
            return "unsat"
        return "unknown"
    return "unknown"


def verify_scheme(profile: dict[str, Any], scheme: dict[str, Any]) -> VerificationResult:
    outcomes: list[ConstraintOutcome] = []
    known_flags = []
    solver = Solver()

    for spec in scheme.get("constraints", []):
        status = _eval_simple(profile, spec)
        outcome = ConstraintOutcome(
            constraint_id=spec["id"],
            explanation=spec.get("explanation") or spec["id"],
            status=status,
            weight=int(spec.get("weight") or 0),
        )
        outcomes.append(outcome)
        flag = Bool(spec["id"])
        if status == "sat":
            solver.add(flag == True)  # noqa: E712
            known_flags.append(flag)
        elif status == "unsat":
            solver.add(flag == False)  # noqa: E712
            known_flags.append(flag)

    failed = [item.explanation for item in outcomes if item.status == "unsat"]
    uncertain = [item.explanation for item in outcomes if item.status == "unknown"]
    satisfied = [item.explanation for item in outcomes if item.status == "sat"]
    required_unknown = [
        spec.get("explanation") or spec["id"]
        for spec in scheme.get("constraints", [])
        if spec.get("required") and _eval_simple(profile, spec) == "unknown"
    ]
    required_failed = [
        spec.get("explanation") or spec["id"]
        for spec in scheme.get("constraints", [])
        if spec.get("required") and _eval_simple(profile, spec) == "unsat"
    ]

    if required_failed or failed and any(
        spec.get("required") and _eval_simple(profile, spec) == "unsat" for spec in scheme.get("constraints", [])
    ):
        overall = "not_eligible"
    elif required_unknown:
        overall = "insufficient_information"
    elif solver.check() == sat and not required_unknown:
        overall = "verified_eligible"
    else:
        overall = "insufficient_information"

    return VerificationResult(
        status=overall,
        outcomes=outcomes,
        failed=failed,
        uncertain=required_unknown or uncertain,
        satisfied=satisfied,
    )
