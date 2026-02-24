from fastapi import APIRouter, HTTPException
from database import get_db
from bson import ObjectId

router = APIRouter()

def fix_id(doc):
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc

@router.get("/{anime_id}")
async def get_episodes(anime_id: str):
    db = get_db()
    episodes = await db.episodes.find(
        {"anime_id": anime_id}
    ).sort("number", 1).to_list(1000)
    if not episodes:
        raise HTTPException(status_code=404, detail="No episodes found")
    return {"results": [fix_id(e) for e in episodes]}

@router.get("/{anime_id}/{episode_number}")
async def get_episode(anime_id: str, episode_number: int):
    db = get_db()
    episode = await db.episodes.find_one({
        "anime_id": anime_id,
        "number": episode_number
    })
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    return fix_id(episode)