from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
from app.config import settings
from app.routes.stats import router as stats_router
from app.services.cache_manager import tokenomics_cache

app = FastAPI(title="Crypto Coin App", description="A FastAPI application for crypto coin stats")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routes
app.include_router(stats_router, prefix="/api/v1", tags=["crypto"])

@app.get("/")
async def root():
    return FileResponse("app/static/index.html")

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Crypto API is running"}

@app.get("/cache/status")
def cache_status():
    """Get Redis cache status and performance metrics"""
    return tokenomics_cache.get_cache_performance(settings.TOKEN_ADDRESS)

@app.get("/cache/performance")
async def cache_performance():
    """Get detailed cache performance metrics including hit rates"""
    return await tokenomics_cache.get_cache_performance(settings.TOKEN_ADDRESS)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)