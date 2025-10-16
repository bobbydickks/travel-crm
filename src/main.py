import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from .routers import auth_router
from .routers import web
from .database import engine, Base
from .settings import settings
import os

# Configure logging  
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Database tables are created via Alembic migrations

# Initialize FastAPI app
app = FastAPI(
    title="Travel CRM API",
    description="Travel CRM platform for managing bookings, clients, and services",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Mount static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
# Include routers
app.include_router(auth_router, prefix="/auth", tags=["authentication"])
app.include_router(web.router, tags=["web"])


@app.get("/", tags=["Root"])
async def root():
    return {"message": "Travel CRM API", "version": "1.0.0"}


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Favicon endpoint"""
    favicon_path = "static/favicon.ico"
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    else:
        # Return a simple 1x1 transparent PNG if no favicon found
        from fastapi.responses import Response
        transparent_png = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\x0f\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x18\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
        return Response(content=transparent_png, media_type="image/png")


@app.get("/robots.txt", include_in_schema=False)
async def robots():
    """Robots.txt for web crawlers"""
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse("User-agent: *\nDisallow: /auth/\nAllow: /docs\nAllow: /health")


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    try:
        # Basic health check - can be extended with DB connectivity check
        return {
            "status": "healthy",
            "environment": settings.environment,
            "service": "travel-crm-api"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unavailable")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
