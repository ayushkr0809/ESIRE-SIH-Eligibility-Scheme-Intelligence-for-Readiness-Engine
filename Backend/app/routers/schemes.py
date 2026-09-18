from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.postgres import get_db
from app.deps import get_current_user, require_admin
from app.models import Application, User
from app.schemas import ApplyRequest, SchemeUpsert
from app.services import catalog
from app.services.matching import evaluate_user

router = APIRouter(prefix="/api", tags=["schemes"])


@router.get("/dashboard")
def dashboard(
    debug: bool = Query(default=False),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return evaluate_user(db, user, include_excluded=debug)


@router.post("/match/reevaluate")
def reevaluate(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return evaluate_user(db, user, include_excluded=True)


@router.get("/schemes/{scheme_id}")
def scheme_detail(scheme_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    result = evaluate_user(db, user)
    for item in result["schemes"]:
        if item["scheme_id"] == scheme_id:
            return item
    scheme = catalog.get_scheme(scheme_id)
    if scheme is None:
        raise HTTPException(status_code=404, detail="Scheme not found")
    raise HTTPException(status_code=404, detail="Scheme is below the display threshold for this profile")


@router.get("/my-schemes")
def my_schemes(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    result = evaluate_user(db, user)
    return {"schemes": [item for item in result["schemes"] if item.get("applied")]}


@router.post("/schemes/{scheme_id}/apply")
def apply_scheme(scheme_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if catalog.get_scheme(scheme_id) is None:
        raise HTTPException(status_code=404, detail="Scheme not found")
    existing = db.query(Application).filter(Application.user_id == user.id, Application.scheme_id == scheme_id).first()
    if existing is None:
        db.add(Application(user_id=user.id, scheme_id=scheme_id))
        db.commit()
    return {"ok": True, "scheme_id": scheme_id}


@router.post("/admin/schemes", dependencies=[Depends(require_admin)])
def admin_upsert(body: SchemeUpsert, db: Session = Depends(get_db)):
    return catalog.upsert_scheme(db, body.model_dump())
