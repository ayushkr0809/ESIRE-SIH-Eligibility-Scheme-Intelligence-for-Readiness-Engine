from app.services.scoring import combine_scores, display_band, document_score, eligibility_score
from app.services.z3_engine import verify_scheme


def _scheme():
    return {
        "id": "t1",
        "name": "Test",
        "constraints": [
            {"id": "age_range", "type": "age_range", "min": 18, "max": 60, "required": True, "weight": 40, "explanation": "Age 18-60"},
            {"id": "income_limit", "type": "max_number", "field": "annual_income", "value": 500000, "required": True, "weight": 30, "explanation": "Income limit"},
            {"id": "occupation", "type": "in_set", "field": "occupation_type", "values": ["entrepreneur"], "required": True, "weight": 30, "explanation": "Must be entrepreneur"},
        ],
        "documents": [
            {"id": "aadhaar", "name": "Aadhaar Card", "weight": 40},
            {"id": "pan", "name": "PAN Card", "weight": 30},
            {"id": "bank", "name": "Bank Passbook / Statement", "weight": 30},
        ],
    }


def test_clearly_eligible():
    result = verify_scheme(
        {"age": 28, "annual_income": 200000, "occupation_type": "entrepreneur", "citizenship": "IN"},
        _scheme(),
    )
    assert result.status == "verified_eligible"
    assert not result.failed


def test_clearly_ineligible():
    result = verify_scheme(
        {"age": 16, "annual_income": 200000, "occupation_type": "entrepreneur"},
        _scheme(),
    )
    assert result.status == "not_eligible"
    assert result.failed


def test_insufficient_information():
    result = verify_scheme({"age": 28}, _scheme())
    assert result.status == "insufficient_information"
    assert result.uncertain


def test_missing_one_document_reduces_readiness_only():
    scheme = _scheme()
    verification = verify_scheme(
        {"age": 28, "annual_income": 200000, "occupation_type": "entrepreneur"},
        scheme,
    )
    elig = eligibility_score(scheme, verification)
    full, *_ = document_score(scheme, {"aadhaar": "uploaded", "pan": "uploaded", "bank": "uploaded"})
    partial, present, missing, _ = document_score(scheme, {"aadhaar": "uploaded", "pan": "uploaded"})
    assert full == 100
    assert partial == 70
    assert missing == ["Bank Passbook / Statement"]
    assert len(present) == 2
    assert combine_scores(elig, partial) < combine_scores(elig, full)
    assert combine_scores(elig, partial) > 50


def test_becomes_ineligible_after_new_information():
    scheme = _scheme()
    before = verify_scheme(
        {"age": 28, "annual_income": 200000, "occupation_type": "entrepreneur"},
        scheme,
    )
    after = verify_scheme(
        {"age": 28, "annual_income": 900000, "occupation_type": "entrepreneur"},
        scheme,
    )
    assert before.status == "verified_eligible"
    assert after.status == "not_eligible"


def test_display_threshold_strictly_greater_than_50():
    assert display_band(50) is None
    assert display_band(49.9) is None
    assert display_band(50.01) == "moderate"
    assert display_band(78) == "strong"


def test_score_exactly_50_is_excluded():
    from app.config import get_settings

    settings = get_settings()
    settings.eligibility_weight = 0.5
    settings.document_weight = 0.5
    assert combine_scores(50, 50) == 50
    assert display_band(combine_scores(50, 50)) is None


def test_high_profile_missing_documents_still_can_display():
    scheme = _scheme()
    verification = verify_scheme(
        {"age": 30, "annual_income": 120000, "occupation_type": "entrepreneur"},
        scheme,
    )
    elig = eligibility_score(scheme, verification)
    docs, *_ = document_score(scheme, {"aadhaar": "uploaded"})
    final = combine_scores(elig, docs)
    assert elig == 100
    assert docs == 40
    assert final > 50
