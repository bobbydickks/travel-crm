"""
Vercel serverless function for Travel CRM API
"""
import sys
import os
from pathlib import Path

# Configure paths for Vercel environment
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

# Change working directory for proper file access
os.chdir(ROOT)

# Try to import and configure the FastAPI app
try:
    from src.main import app
    # For Vercel, the handler should be the FastAPI app instance
    handler = app
except Exception as e:
    # Fallback error handler
    from fastapi import FastAPI
    
    fallback_app = FastAPI(title="Travel CRM API - Error")
    
    @fallback_app.get("/")
    async def error_info():
        return {
            "error": "Application failed to initialize",
            "details": str(e),
            "message": "Please check server logs for more information"
        }
    
    handler = fallback_app
