from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Travel CRM API",
    description="Travel Customer Relationship Management System",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {
        "message": "Travel CRM API is running",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc", 
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "travel-crm",
        "timestamp": "2025-10-17"
    }

@app.get("/docs-info")
async def docs_info():
    return {
        "message": "API Documentation Available",
        "swagger_ui": "/docs",
        "redoc": "/redoc",
        "openapi_json": "/openapi.json",
        "note": "FastAPI auto-generated documentation"
    }
