from fastapi import APIRouter, HTTPException
from database import get_db
from bson import ObjectId

router = APIRouter()

def fix_id(doc):
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc

@router.get("/")
async def get_all_anime(page: int = 1, limit: int = 20):
    db = get_db()
    skip = (page - 1) * limit
    anime_list = await db.anime.find().skip(skip).limit(limit).to_list(limit)
    total = await db.anime.count_documents({})
    return {
        "total": total,
        "page": page,
        "results": [fix_id(a) for a in anime_list]
    }

@router.get("/search")
async def search_anime(q: str):
    db = get_db()
    results = await db.anime.find({
        "title": {"$regex": q, "$options": "i"}
    }).to_list(20)
    return {"results": [fix_id(a) for a in results]}

@router.get("/trending")
async def get_trending():
    db = get_db()
    results = await db.anime.find(
        {"status": "airing"}
    ).sort("views", -1).limit(20).to_list(20)
    return {"results": [fix_id(a) for a in results]}

@router.get("/{anime_id}")
async def get_anime(anime_id: str):
    db = get_db()
    anime = await db.anime.find_one({"_id": ObjectId(anime_id)})
    if not anime:
        raise HTTPException(status_code=404, detail="Anime not found")
    return fix_id(anime)