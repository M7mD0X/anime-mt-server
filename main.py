from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import anime, episodes, admin
from database import connect_db

app = FastAPI(title="Anime MT API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await connect_db()

@app.get("/")
async def root():
    return {"message": "Anime MT API is running! 🚀"}

app.include_router(anime.router, prefix="/anime", tags=["Anime"])
app.include_router(episodes.router, prefix="/episodes", tags=["Episodes"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])