from pathlib import Path
import shutil

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import mongo
from app.db.postgres import get_db
from app.deps import get_current_user
from app.models import Application, MatchResult, Profile, User, UserDocument
from app.schemas import LanguageRequest, ProfileUpdate
from app.services.extractor import extract_profile
from app.services.matching import apply_extraction, evaluate_user, profile_completeness, profile_to_dict

router = APIRouter(prefix="/api", tags=["users"])
settings = get_settings()


@router.get("/me")
def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.profile is None:
        db.add(Profile(user_id=user.id, citizenship="IN"))
        db.commit()
        db.refresh(user)
    pdata = profile_to_dict(user.profile)
    return {
        "id": user.id,
        "phone": user.phone,
        "name": user.name,
        "language": user.language,
        "profile": pdata,
        **profile_completeness(pdata),
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
    pdata = profile_to_dict(user.profile)
    return {
        "id": user.id,
        "phone": user.phone,
        "name": user.name,
        "language": user.language,
        "profile": pdata,
        **profile_completeness(pdata),
    }


@router.delete("/me")
def delete_account(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Permanently delete the account and everything tied to it: profile,
    uploaded document records, cached match results, applications, the
    user's uploaded files on disk, and any cached extraction data. This
    cannot be undone."""
    user_id = user.id

    db.query(Application).filter(Application.user_id == user_id).delete()
    db.query(MatchResult).filter(MatchResult.user_id == user_id).delete()
    db.query(UserDocument).filter(UserDocument.user_id == user_id).delete()
    if user.profile is not None:
        db.delete(user.profile)
    db.delete(user)
    db.commit()

    # Best-effort cleanup of data outside the SQL database — a failure here
    # must not undo the account deletion that already succeeded above.
    try:
        mongo.delete_prefix("extractions", f"user-{user_id}")
        mongo.delete_prefix("extractions", f"doc-{user_id}-")
    except Exception:  # noqa: BLE001
        pass
    try:
        shutil.rmtree(Path(settings.upload_dir) / str(user_id), ignore_errors=True)
    except Exception:  # noqa: BLE001
        pass

    return {"deleted": True}
