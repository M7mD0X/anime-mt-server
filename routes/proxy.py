from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse, Response
import httpx
import re

router = APIRouter()

HEADERS = {
    "Referer": "https://hianime.to",
    "Origin": "https://hianime.to",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

@router.get("/proxy/video")
async def proxy_video(url: str, request: Request):
    base_url = str(request.base_url)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADERS)
        content = response.text
        
        # Get base URL for segments
        url_base = url.rsplit('/', 1)[0] + '/'
        
        # Rewrite segment URLs in m3u8
        lines = content.split('\n')
        new_lines = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                if line.startswith('http'):
                    segment_url = line
                else:
                    segment_url = url_base + line
                proxied = f"{base_url}proxy/segment?url={httpx.URL(segment_url)}"
                new_lines.append(proxied)
            else:
                new_lines.append(line)
        
        new_content = '\n'.join(new_lines)
        
        return Response(
            content=new_content,
            media_type="application/vnd.apple.mpegurl",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Cache-Control": "no-cache",
            }
        )

@router.get("/proxy/segment")
async def proxy_segment(url: str):
    async def stream():
        async with httpx.AsyncClient() as client:
            async with client.stream("GET", url, headers=HEADERS) as response:
                async for chunk in response.aiter_bytes():
                    yield chunk
    
    return StreamingResponse(
        stream(),
        media_type="video/MP2T",
        headers={"Access-Control-Allow-Origin": "*"}
    )