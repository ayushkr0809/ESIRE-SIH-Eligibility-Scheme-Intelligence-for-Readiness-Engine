from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.postgres import get_db
from app.models import Profile, User
from app.schemas import OtpVerifyRequest, PhoneRequest, SignupRequest
from app.security import create_access_token
from app.services.extractor import extract_profile
from app.services.matching import apply_extraction, evaluate_user
from app.services.otp import issue_otp, verify_otp

router = APIRouter(prefix="/api/auth", tags=["auth"])
settings = get_settings()


def _token_payload(user: User) -> dict:
    return {
        "access_token": create_access_token(user.id, user.phone),
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "phone": user.phone,
            "name": user.name,
            "language": user.language,
        },
    }


@router.post("/signup")
def signup(body: SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.phone == body.phone).first()
    if existing:
        raise HTTPException(status_code=409, detail="An account with this mobile number already exists")
    user = User(phone=body.phone, name=body.name.strip(), language=body.language or "en")
    db.add(user)
    db.flush()
    profile = Profile(user_id=user.id, about_text=body.about_text or "", citizenship="IN")
    if body.about_text:
        extracted, source = extract_profile(body.about_text, body.language or "en")
        apply_extraction(profile, extracted, source)
        if extracted.get("name") and not user.name:
            user.name = extracted["name"]
    db.add(profile)
    db.commit()
    db.refresh(user)
    evaluate_user(db, user)
    return _token_payload(user)


@router.post("/otp/request")
def request_otp(body: PhoneRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == body.phone).first()
    if user is None:
        raise HTTPException(status_code=404, detail="No account found for this mobile number")
    code = issue_otp(db, body.phone, purpose="login")
    payload = {"ok": True, "message": "OTP sent"}
    if settings.otp_echo:
        payload["dev_otp"] = code
        payload["dev_note"] = "Mock OTP provider. Replace OtpProvider.send with SMS in production."
    return payload


@router.post("/otp/verify")
def otp_verify(body: OtpVerifyRequest, db: Session = Depends(get_db)):
    if not verify_otp(db, body.phone, body.otp, purpose="login"):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    user = db.query(User).filter(User.phone == body.phone).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return _token_payload(user)
