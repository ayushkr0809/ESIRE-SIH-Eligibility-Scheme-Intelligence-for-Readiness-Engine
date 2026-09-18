from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import mongo
from app.db.postgres import get_db
from app.deps import get_current_user
from app.models import User, UserDocument
from app.services.catalog import all_schemes
from app.services.matching import evaluate_user
from app.services.ollama import ollama_service

router = APIRouter(prefix="/api/documents", tags=["documents"])
settings = get_settings()


def _catalogue_docs() -> list[dict]:
    seen = {}
    for scheme in all_schemes():
        for doc in scheme.get("documents") or []:
            seen[doc["id"]] = {
                "id": doc["id"],
                "name": doc.get("name"),
                "note": doc.get("note") or "",
                "proves": doc.get("proves") or [],
            }
    return list(seen.values())


@router.get("")
def list_documents(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing = {row.doc_type: row for row in db.query(UserDocument).filter(UserDocument.user_id == user.id).all()}
    items = []
    for spec in _catalogue_docs():
        row = existing.get(spec["id"])
        items.append(
            {
                **spec,
                "status": row.status if row else "missing",
                "original_name": row.original_name if row else "",
                "updated_at": row.updated_at.isoformat() if row else None,
            }
        )
    return {"documents": items}


@router.post("/upload")
async def upload_document(
    doc_type: str = Form(...),
    file: UploadFile | None = File(default=None),
    mark_ready: bool = Form(default=True),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    allowed = {item["id"] for item in _catalogue_docs()}
    if doc_type not in allowed:
        raise HTTPException(status_code=400, detail="Unknown document type")
    upload_root = Path(settings.upload_dir) / str(user.id)
    upload_root.mkdir(parents=True, exist_ok=True)
    stored_path = ""
    original_name = ""
    if file is not None:
        original_name = file.filename or f"{doc_type}.bin"
        dest = upload_root / f"{doc_type}_{original_name}"
        dest.write_bytes(await file.read())
        stored_path = str(dest)
    row = db.query(UserDocument).filter(UserDocument.user_id == user.id, UserDocument.doc_type == doc_type).first()
    if row is None:
        row = UserDocument(user_id=user.id, doc_type=doc_type)
        db.add(row)
    row.original_name = original_name or row.original_name
    row.stored_path = stored_path or row.stored_path
    row.status = "uploaded" if mark_ready else "missing"
    if file is not None:
        extracted = ollama_service.extract_profile(
            f"Document type {doc_type} uploaded as {original_name}. Treat as user-supplied evidence, not verified government proof.",
            user.language,
        )
        if extracted:
            row.status = "extracted"
            mongo.upsert("extractions", f"doc-{user.id}-{doc_type}", {"extracted": extracted, "status": "extracted"})
        else:
            mongo.upsert(
                "extractions",
                f"doc-{user.id}-{doc_type}",
                {"status": "uploaded", "note": "Stored. Automated verification is not claimed."},
            )
    db.commit()
    evaluate_user(db, user)
    return {"doc_type": doc_type, "status": row.status}


@router.post("/{doc_type}/status")
def set_status(doc_type: str, status: str = "uploaded", user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if status not in {"missing", "uploaded", "extracted", "verified", "invalid"}:
        raise HTTPException(status_code=400, detail="Invalid status")
    row = db.query(UserDocument).filter(UserDocument.user_id == user.id, UserDocument.doc_type == doc_type).first()
    if row is None:
        row = UserDocument(user_id=user.id, doc_type=doc_type)
        db.add(row)
    if status == "missing":
        db.delete(row)
        db.commit()
        evaluate_user(db, user)
        return {"doc_type": doc_type, "status": "missing"}
    row.status = status
    db.commit()
    evaluate_user(db, user)
    return {"doc_type": doc_type, "status": row.status}
