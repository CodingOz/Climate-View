from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.database import engine, Base
from app.routers import threats, companies, organisations, campaigns
import app.models  # ensures all models are registered


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Climate Threat & Resistance Tracker API",
    description="A living registry of environmental threats and the movements opposing them.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(threats.router)
app.include_router(companies.router)
app.include_router(organisations.router)
app.include_router(campaigns.router)


@app.get("/")
async def root():
    return {"message": "Climate Threat & Resistance Tracker API", "docs": "/docs"}