from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import logging

from ..core.database import get_db
from ..services.clio_service import ClioService

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/auth")
async def get_auth_url():
    """Get Clio OAuth authorization URL"""
    try:
        clio_service = ClioService()
        auth_url = clio_service.get_auth_url()
        return {"auth_url": auth_url}
    
    except Exception as e:
        logger.error(f"Clio auth URL error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test")
async def test_clio_connection(db: Session = Depends(get_db)):
    """Test Clio API connection"""
    try:
        clio_service = ClioService()
        result = await clio_service.test_connection(db)
        
        return {
            "connected": result.get("connected", False),
            "message": result.get("message", ""),
            "user": result.get("user")
        }
    
    except Exception as e:
        logger.error(f"Clio test error: {e}")
        return {
            "connected": False,
            "message": f"Connection test failed: {str(e)}"
        }

@router.post("/push-entries")
async def push_time_entries(db: Session = Depends(get_db)):
    """Push time entries to Clio"""
    try:
        clio_service = ClioService()
        result = await clio_service.push_time_entries(db)
        
        return {
            "success": result.get("success", False),
            "pushed_count": result.get("pushed_count", 0),
            "errors": result.get("errors", []),
            "message": result.get("message", "")
        }
    
    except Exception as e:
        logger.error(f"Clio push error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/matters")
async def get_matters(db: Session = Depends(get_db)):
    """Get matters from Clio"""
    try:
        clio_service = ClioService()
        matters = await clio_service.get_matters(db)
        
        return {"success": True, "matters": matters}
    
    except Exception as e:
        logger.error(f"Error fetching matters: {e}")
        raise HTTPException(status_code=500, detail=str(e))
