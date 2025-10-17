"""
Vercel serverless function for Travel CRM API
Minimal version that works without complex imports
"""
try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import JSONResponse
    
    # Create a minimal FastAPI app for Vercel
    app = FastAPI(
        title="Travel CRM API",
        description="Travel Customer Relationship Management System",
        version="1.0.0"
    )
    
    @app.get("/")
    async def root():
        return {"message": "Travel CRM API is running", "version": "1.0.0"}
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "travel-crm"}
    
    @app.get("/docs-info")
    async def docs_info():
        return {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json"
        }
    
    # For Vercel
    handler = app
    
except ImportError as e:
    # Fallback if FastAPI not available
    def handler(event, context):
        return {
            "statusCode": 500,
            "body": f"Module import error: {str(e)}. Check requirements.txt and build logs."
        }
