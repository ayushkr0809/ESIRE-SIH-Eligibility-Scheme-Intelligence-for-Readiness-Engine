from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.postgres import get_db
from app.deps import get_current_user
from app.models import Profile, User
from app.schemas import LanguageRequest, ProfileUpdate
from app.services.extractor import extract_profile
from app.services.matching import apply_extraction, evaluate_user, profile_to_dict

router = APIRouter(prefix="/api", tags=["users"])


@router.get("/me")
def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.profile is None:
        db.add(Profile(user_id=user.id, citizenship="IN"))
        db.commit()
        db.refresh(user)
    return {
        "id": user.id,
        "phone": user.phone,
        "name": user.name,
        "language": user.language,
        "profile": profile_to_dict(user.profile),
    }


@router.put("/me/language")
def update_language(body: LanguageRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user.language = body.language
    db.commit()
    return {"language": user.language}


@router.put("/me/profile")
def update_profile(body: ProfileUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.profile is None:
        user.profile = Profile(user_id=user.id, citizenship="IN")
        db.add(user.profile)
        db.flush()
    data = body.model_dump(exclude_unset=True)
    if "name" in data and data["name"] is not None:
        user.name = data.pop("name")
    if "language" in data and data["language"] is not None:
        user.language = data.pop("language")
    about = data.get("about_text")
    for key, value in data.items():
        setattr(user.profile, key, value)
    if about:
        extracted, source = extract_profile(about, user.language)
        apply_extraction(user.profile, extracted, source)
    db.commit()
    evaluate_user(db, user)
    db.refresh(user)
    return {"id": user.id, "phone": user.phone, "name": user.name, "language": user.language, "profile": profile_to_dict(user.profile)}
