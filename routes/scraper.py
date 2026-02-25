from fastapi import APIRouter, HTTPException
import httpx
from bs4 import BeautifulSoup
import re

router = APIRouter()

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'ar,en;q=0.9',
    'Referer': 'https://witanime.life/',
}

@router.get("/debug")
async def debug(q: str):
    try:
        async with httpx.AsyncClient(headers=HEADERS, timeout=15, follow_redirects=True) as client:
            response = await client.get(f'https://witanime.life/?search_param=animes&s={q}')
            soup = BeautifulSoup(response.text, 'lxml')
            # نجيب كل الـ classes الموجودة
            classes = set()
            for tag in soup.find_all(class_=True):
                for c in tag.get('class', []):
                    classes.add(c)
            return {
                "status": response.status_code,
                "url": str(response.url),
                "classes": list(classes)[:50],
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_witanime(q: str):
    try:
        async with httpx.AsyncClient(headers=HEADERS, timeout=15, follow_redirects=True) as client:
            response = await client.get(f'https://witanime.life/?search_param=animes&s={q}')
            soup = BeautifulSoup(response.text, 'lxml')
            results = []
            for item in soup.select('.anime-card-container')[:10]:
                title_el = item.select_one('.anime-card-title h3')
                link_el = item.select_one('a')
                img_el = item.select_one('img')
                if title_el and link_el:
                    results.append({
                        'title': title_el.text.strip(),
                        'url': link_el.get('href', ''),
                        'cover': img_el.get('src', '') if img_el else '',
                    })
            return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/episodes")
async def get_episodes_witanime(url: str):
    try:
        async with httpx.AsyncClient(headers=HEADERS, timeout=15, follow_redirects=True) as client:
            response = await client.get(url)
            soup = BeautifulSoup(response.text, 'lxml')
            episodes = []
            for ep in soup.select('.episodes-card-title a'):
                episodes.append({
                    'title': ep.text.strip(),
                    'url': ep.get('href', ''),
                })
            return {"results": episodes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/video")
async def get_video_url(url: str):
    try:
        async with httpx.AsyncClient(headers=HEADERS, timeout=15, follow_redirects=True) as client:
            response = await client.get(url)
            soup = BeautifulSoup(response.text, 'lxml')
            video_urls = []
            for video in soup.select('video source, video'):
                src = video.get('src', '')
                if src and '.mp4' in src:
                    video_urls.append({'quality': 'default', 'url': src})
            iframes = soup.select('iframe')
            for iframe in iframes:
                src = iframe.get('src', '')
                if src:
                    video_urls.append({'quality': 'iframe', 'url': src})
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    mp4_urls = re.findall(r'https?://[^\s"\']+\.mp4[^\s"\']*', script.string)
                    for u in mp4_urls:
                        video_urls.append({'quality': 'auto', 'url': u})
            if not video_urls:
                raise HTTPException(status_code=404, detail="No video found")
            return {"results": video_urls}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))