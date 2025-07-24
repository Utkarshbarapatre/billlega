from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import logging

from ..core.database import get_db
from ..services.summarizer_service import SummarizerService
from ..models.email import Email

router = APIRouter()
logger = logging.getLogger(__name__)

class SummaryUpdate(BaseModel):
    billing_hours: float
    billing_description: str
    summary: str

@router.post("/generate")
async def generate_summaries(db: Session = Depends(get_db)):
    """Generate AI summaries for emails"""
    try:
        summarizer_service = SummarizerService()
        result = await summarizer_service.generate_summaries(db)
        
        return {
            "success": result.get("success", False),
            "summaries_generated": result.get("summaries_generated", 0),
            "errors": result.get("errors", []),
            "message": result.get("message", "")
        }
    
    except Exception as e:
        logger.error(f"Summary generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summaries")
async def get_summaries(db: Session = Depends(get_db)):
    """Get all generated summaries"""
    try:
        emails = db.query(Email).filter(Email.summary.isnot(None)).order_by(Email.date_sent.desc()).all()
        
        summaries = []
        for email in emails:
            summaries.append({
                "id": email.id,
                "email_id": email.gmail_id,
                "subject": email.subject,
                "summary": email.summary,
                "billing_hours": email.billing_hours or 0.25,
                "billing_description": email.billing_description or "",
                "date_sent": email.date_sent.isoformat() if email.date_sent else None,
                "pushed_to_clio": email.pushed_to_clio
            })
        
        return {"success": True, "summaries": summaries}
    
    except Exception as e:
        logger.error(f"Error fetching summaries: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/summaries/{summary_id}")
async def update_summary(
    summary_id: int,
    summary_update: SummaryUpdate,
    db: Session = Depends(get_db)
):
    """Update a summary"""
    try:
        email = db.query(Email).filter(Email.id == summary_id).first()
        
        if not email:
            raise HTTPException(status_code=404, detail="Summary not found")
        
        email.billing_hours = summary_update.billing_hours
        email.billing_description = summary_update.billing_description
        email.summary = summary_update.summary
        
        db.commit()
        
        return {"success": True, "message": "Summary updated successfully"}
    
    except Exception as e:
        logger.error(f"Error updating summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
