from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from slowapi import Limiter, _rate_limit_exceeded_handler
from app.routers import threats, companies, organisations, campaigns, auth, analytics, search
import app.models
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.limiter import limiter



@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Climate Threat & Resistance Tracker API",
    description="A living registry of environmental threats and the movements opposing them.",
    version="1.0.0",
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(threats.router)
app.include_router(companies.router)
app.include_router(organisations.router)
app.include_router(campaigns.router)
app.include_router(analytics.router)
app.include_router(search.router)


@app.get("/")
async def root():
    return {"message": "Climate Threat & Resistance Tracker API", "docs": "/docs"}