from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
import os
from dotenv import load_dotenv
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from .routers import gmail, clio, summarizer, extension
from .core.config import settings
from .core.database import init_db, get_db, ClioToken
from .services.clio_service import ClioService
from .utils.logging_config import setup_logging

# Load environment variables
load_dotenv()

# Setup logging
setup_logging(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up Legal Billing Email Summarizer")
    logger.info(f"Environment: {'Production' if not settings.debug else 'Development'}")
    logger.info(f"Port: {settings.port}")
    
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Legal Billing Email Summarizer")

app = FastAPI(
    title="Legal Billing Email Summarizer",
    description="Automatically fetch Gmail emails, generate AI summaries, and integrate with Clio",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else [
        "https://gracious-celebration.railway.internal",
        "https://*.railway.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(gmail.router, prefix="/api/gmail", tags=["Gmail"])
app.include_router(clio.router, prefix="/api/clio", tags=["Clio"])
app.include_router(summarizer.router, prefix="/api/summarizer", tags=["Summarizer"])
app.include_router(extension.router, prefix="/api/extension", tags=["Extension"])

# OAuth callback route
@app.get("/callback")
async def oauth_callback(code: str = None, error: str = None, db: Session = Depends(get_db)):
    """Handle OAuth callback from Clio"""
    try:
        logger.info(f"OAuth callback received - code: {'present' if code else 'missing'}, error: {error}")
        
        if error:
            logger.error(f"OAuth error: {error}")
            return RedirectResponse(url="/?clio_error=true")
        
        if not code:
            logger.error("No authorization code received")
            return RedirectResponse(url="/?clio_error=no_code")
        
        # Create Clio service and exchange code for token
        clio_service = ClioService()
        token_data = await clio_service.exchange_code_for_token(code)
        
        # Store token in database
        # First, delete any existing tokens
        db.query(ClioToken).delete()
        
        clio_token = ClioToken(
            access_token=token_data['access_token'],
            refresh_token=token_data.get('refresh_token', ''),
            expires_at=None
        )
        db.add(clio_token)
        db.commit()
        
        logger.info("Clio token stored successfully")
        return RedirectResponse(url="/?clio_connected=true")
        
    except Exception as e:
        logger.error(f"OAuth callback error: {e}")
        return RedirectResponse(url=f"/?clio_error={str(e)}")

@app.get("/api/status")
async def get_status(db: Session = Depends(get_db)):
    """Get connection status"""
    try:
        # Check Gmail connection
        gmail_connected = (
            os.path.exists('client_secret.json') or 
            os.path.exists(settings.google_client_secret_file)
        )
        
        # Check Clio connection
        clio_token = db.query(ClioToken).first()
        clio_connected = clio_token is not None
        
        return {
            "gmail_connected": gmail_connected,
            "clio_connected": clio_connected,
            "status": "healthy",
            "environment": "production" if not settings.debug else "development"
        }
    except Exception as e:
        logger.error(f"Status check error: {e}")
        return {
            "gmail_connected": False,
            "clio_connected": False,
            "status": "error",
            "message": str(e)
        }

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    return {
        "status": "healthy",
        "service": "Legal Billing Email Summarizer",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "port": settings.port
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Legal Billing Email Summarizer API",
        "version": "1.0.0",
        "docs": "/docs" if settings.debug else "Documentation disabled in production",
        "health": "/health",
        "status": "/api/status"
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return {"error": "Not found", "path": str(request.url)}

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    logger.error(f"Internal server error: {exc}")
    return {"error": "Internal server error", "message": str(exc)}

def main():
    """Main function to run the application"""
    # Get port from environment variable, default to 8000
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    logger.info(f"Starting server on {host}:{port}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Environment: {os.getenv('RAILWAY_ENVIRONMENT', 'development')}")
    
    uvicorn.run(
        "backend.main:app",
        host=host,
        port=port,
        reload=settings.debug,
        log_level="info"
    )

if __name__ == "__main__":
    main()
