from fastapi import APIRouter, HTTPException, Header
from database import get_db
from bson import ObjectId
from pydantic import BaseModel
from typing import Optional, List
import os

router = APIRouter()

ADMIN_KEY = os.getenv("ADMIN_KEY", "anime-mt-secret")

def check_auth(x_admin_key: str):
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

def fix_id(doc):
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc
    
class AnimeModel(BaseModel):
    title: str
    title_arabic: Optional[str] = ""
    description: Optional[str] = ""
    description_arabic: Optional[str] = ""
    cover: Optional[str] = ""
    banner: Optional[str] = ""
    status: Optional[str] = "airing"
    type: Optional[str] = "TV"
    episodes_count: Optional[int] = 0
    genres: Optional[List[str]] = []
    year: Optional[int] = None
    score: Optional[float] = None
    views: Optional[int] = 0
    aniwatch_id: Optional[str] = ""


class EpisodeModel(BaseModel):
    anime_id: str
    number: int
    title: Optional[str] = ""
    title_arabic: Optional[str] = ""
    thumbnail: Optional[str] = ""
    video_url: Optional[str] = ""
    video_url_arabic: Optional[str] = ""
    duration: Optional[int] = 0

# Anime endpoints
@router.post("/anime")
async def add_anime(anime: AnimeModel, x_admin_key: str = Header(...)):
    check_auth(x_admin_key)
    db = get_db()
    result = await db.anime.insert_one(anime.dict())
    return {"id": str(result.inserted_id), "message": "Anime added!"}

@router.put("/anime/{anime_id}")
async def update_anime(anime_id: str, anime: AnimeModel, x_admin_key: str = Header(...)):
    check_auth(x_admin_key)
    db = get_db()
    await db.anime.update_one(
        {"_id": ObjectId(anime_id)},
        {"$set": anime.dict()}
    )
    return {"message": "Anime updated!"}

@router.delete("/anime/{anime_id}")
async def delete_anime(anime_id: str, x_admin_key: str = Header(...)):
    check_auth(x_admin_key)
    db = get_db()
    await db.anime.delete_one({"_id": ObjectId(anime_id)})
    await db.episodes.delete_many({"anime_id": anime_id})
    return {"message": "Anime deleted!"}

# Episode endpoints
@router.post("/episode")
async def add_episode(episode: EpisodeModel, x_admin_key: str = Header(...)):
    check_auth(x_admin_key)
    db = get_db()
    result = await db.episodes.insert_one(episode.dict())
    await db.anime.update_one(
        {"_id": ObjectId(episode.anime_id)},
        {"$inc": {"episodes_count": 1}}
    )
    return {"id": str(result.inserted_id), "message": "Episode added!"}

@router.put("/episode/{episode_id}")
async def update_episode(episode_id: str, episode: EpisodeModel, x_admin_key: str = Header(...)):
    check_auth(x_admin_key)
    db = get_db()
    await db.episodes.update_one(
        {"_id": ObjectId(episode_id)},
        {"$set": episode.dict()}
    )
    return {"message": "Episode updated!"}

@router.delete("/episode/{episode_id}")
async def delete_episode(episode_id: str, x_admin_key: str = Header(...)):
    check_auth(x_admin_key)
    db = get_db()
    episode = await db.episodes.find_one({"_id": ObjectId(episode_id)})
    if episode:
        await db.anime.update_one(
            {"_id": ObjectId(episode["anime_id"])},
            {"$inc": {"episodes_count": -1}}
        )
    await db.episodes.delete_one({"_id": ObjectId(episode_id)})
    return {"message": "Episode deleted!"}