from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import httpx

router = APIRouter()

@router.get("/proxy/video")
async def proxy_video(url: str):
    headers = {
        "Referer": "https://hianime.to",
        "Origin": "https://hianime.to",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }
    
    async def stream():
        async with httpx.AsyncClient() as client:
            async with client.stream("GET", url, headers=headers) as response:
                async for chunk in response.aiter_bytes():
                    yield chunk
    
    return StreamingResponse(stream(), media_type="application/vnd.apple.mpegurl")