from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import router as api_v1_router
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-Powered Synthetic User Research Platform API - Generate one or more synthetic user personas.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc")
# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routes (Both Root Level /generate-persona & Versioned /api/v1/generate-persona)
app.include_router(api_v1_router)
app.include_router(api_v1_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health Check"], summary="Service Health Check")
async def health_check():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
