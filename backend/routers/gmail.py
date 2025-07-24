from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime, timedelta

from ..core.database import get_db
from ..services.gmail_service import GmailService
from ..models.email import Email

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/authenticate")
async def authenticate_gmail():
    """Authenticate with Gmail"""
    try:
        gmail_service = GmailService()
        result = await gmail_service.authenticate()
        
        if result.get("success"):
            return {"success": True, "message": "Gmail authenticated successfully"}
        else:
            return {"success": False, "message": result.get("message", "Authentication failed")}
    
    except Exception as e:
        logger.error(f"Gmail authentication error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/emails")
async def fetch_emails(
    days_back: int = 7,
    max_results: int = 100,
    db: Session = Depends(get_db)
):
    """Fetch emails from Gmail"""
    try:
        gmail_service = GmailService()
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Fetch emails
        emails = await gmail_service.fetch_emails(
            start_date=start_date,
            end_date=end_date,
            max_results=max_results
        )
        
        # Store emails in database
        new_emails = 0
        stored_emails = []
        
        for email_data in emails:
            # Check if email already exists
            existing_email = db.query(Email).filter(Email.gmail_id == email_data["id"]).first()
            
            if not existing_email:
                email = Email(
                    gmail_id=email_data["id"],
                    subject=email_data.get("subject", ""),
                    sender=email_data.get("sender", ""),
                    recipient=email_data.get("recipient", ""),
                    body=email_data.get("body", ""),
                    date_sent=email_data.get("date_sent"),
                    thread_id=email_data.get("thread_id")
                )
                db.add(email)
                new_emails += 1
            else:
                email = existing_email
            
            stored_emails.append({
                "id": email.gmail_id,
                "subject": email.subject,
                "sender": email.sender,
                "recipient": email.recipient,
                "body": email.body,
                "date_sent": email.date_sent.isoformat() if email.date_sent else None,
                "summary": email.summary,
                "pushed_to_clio": email.pushed_to_clio
            })
        
        db.commit()
        
        return {
            "success": True,
            "emails_fetched": len(emails),
            "new_emails": new_emails,
            "emails": stored_emails
        }
    
    except Exception as e:
        logger.error(f"Email fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/emails/stored")
async def get_stored_emails(db: Session = Depends(get_db)):
    """Get stored emails from database"""
    try:
        emails = db.query(Email).order_by(Email.date_sent.desc()).all()
        
        email_list = []
        for email in emails:
            email_list.append({
                "id": email.gmail_id,
                "subject": email.subject,
                "sender": email.sender,
                "recipient": email.recipient,
                "body": email.body,
                "date_sent": email.date_sent.isoformat() if email.date_sent else None,
                "summary": email.summary,
                "billing_hours": email.billing_hours,
                "billing_description": email.billing_description,
                "pushed_to_clio": email.pushed_to_clio
            })
        
        return {"success": True, "emails": email_list}
    
    except Exception as e:
        logger.error(f"Error fetching stored emails: {e}")
        raise HTTPException(status_code=500, detail=str(e))
