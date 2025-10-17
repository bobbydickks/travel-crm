"""
Vercel serverless function for Travel CRM API
Pure Python HTTP handler without FastAPI dependencies
"""

def handler(event):
    """
    Simple HTTP handler for Vercel
    """
    # Handle different HTTP methods and paths
    method = event.get('httpMethod', 'GET')
    path = event.get('path', '/')
    
    # Response headers
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }
    
    # Handle preflight OPTIONS requests
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    # Route handling
    if path == '/' or path == '':
        body = {
            "message": "Travel CRM API is running",
            "version": "1.0.0",
            "status": "active",
            "endpoints": {
                "docs": "/docs-info",
                "health": "/health",
                "api_info": "/"
            }
        }
    elif path == '/health':
        body = {
            "status": "healthy",
            "service": "travel-crm",
            "timestamp": "2025-10-17"
        }
    elif path == '/docs-info':
        body = {
            "message": "API Documentation",
            "note": "This is a minimal API version for demo purposes",
            "available_endpoints": [
                "GET /",
                "GET /health", 
                "GET /docs-info"
            ],
            "full_api": "Coming soon with database integration"
        }
    else:
        body = {
            "error": "Endpoint not found",
            "path": path,
            "method": method,
            "available_paths": ["/", "/health", "/docs-info"]
        }
        return {
            'statusCode': 404,
            'headers': headers,
            'body': str(body).replace("'", '"')
        }
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': str(body).replace("'", '"')
    }
