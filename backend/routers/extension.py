from fastapi import APIRouter, HTTPException
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/status")
async def extension_status():
    """Check extension status"""
    return {
        "status": "active",
        "message": "Extension API is running",
        "endpoints": {
            "capture": "/api/extension/capture",
            "status": "/api/extension/status"
        }
    }

@router.post("/capture")
async def capture_email(email_data: dict):
    """Capture email from Chrome extension"""
    try:
        # Process email data from extension
        logger.info(f"Received email from extension: {email_data.get('subject', 'No subject')}")
        
        # Here you would process and store the email
        # This is a placeholder for the actual implementation
        
        return {
            "success": True,
            "message": "Email captured successfully",
            "email_id": email_data.get("id")
        }
    
    except Exception as e:
        logger.error(f"Extension capture error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
