from fastapi import APIRouter, Query
from app.core.database import get_db
from bson import ObjectId

router = APIRouter()


def serialize(doc):
    doc["id"] = str(doc.pop("_id"))
    if "created_at" in doc:
        doc["created_at"] = doc["created_at"].isoformat()
    return doc


@router.get("/")
async def get_history(
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
    scan_type: str = Query(None),
):
    db = get_db()
    query = {}
    if scan_type:
        query["scan_type"] = scan_type
    cursor = db.scan_history.find(query).sort("created_at", -1).skip(skip).limit(limit)
    docs = await cursor.to_list(length=limit)
    return [serialize(d) for d in docs]


@router.delete("/{item_id}")
async def delete_history_item(item_id: str):
    db = get_db()
    result = await db.scan_history.delete_one({"_id": ObjectId(item_id)})
    return {"deleted": result.deleted_count > 0}


@router.delete("/")
async def clear_history():
    db = get_db()
    result = await db.scan_history.delete_many({})
    return {"deleted_count": result.deleted_count}
