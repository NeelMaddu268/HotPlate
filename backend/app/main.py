from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import sms, search
from app.core.db import init_db

app = FastAPI(
    title="HotPlate AI Backend",
    description="FastAPI backend for processing Twilio SMS deals",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    await init_db()

app.include_router(sms.router)
app.include_router(search.router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
