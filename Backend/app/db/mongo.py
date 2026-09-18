from __future__ import annotations

from typing import Any

from app.config import get_settings

settings = get_settings()

_memory: dict[str, dict[str, dict[str, Any]]] = {
    "schemes": {},
    "extractions": {},
    "ai_metadata": {},
}

_client = None
_db = None
mongo_mode = "memory"


def init_mongo() -> str:
    global _client, _db, mongo_mode
    try:
        from pymongo import MongoClient

        client = MongoClient(settings.mongo_uri, serverSelectionTimeoutMS=1500)
        client.admin.command("ping")
        _client = client
        _db = client[settings.mongo_db]
        mongo_mode = "mongo"
        return mongo_mode
    except Exception:
        if not settings.allow_inmemory_fallback:
            raise
        mongo_mode = "memory"
        return mongo_mode


def _col(name: str):
    if _db is not None:
        return _db[name]
    return None


def upsert(collection: str, key: str, document: dict[str, Any]) -> None:
    payload = {**document, "_id": key}
    col = _col(collection)
    if col is not None:
        col.replace_one({"_id": key}, payload, upsert=True)
        return
    _memory.setdefault(collection, {})[key] = payload


def find_one(collection: str, key: str) -> dict[str, Any] | None:
    col = _col(collection)
    if col is not None:
        return col.find_one({"_id": key})
    return _memory.get(collection, {}).get(key)


def find_all(collection: str) -> list[dict[str, Any]]:
    col = _col(collection)
    if col is not None:
        return list(col.find({}))
    return list(_memory.get(collection, {}).values())
