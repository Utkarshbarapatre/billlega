import os
import httpx
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
import logging

from ..core.database import ClioToken
from ..models.email import Email
from ..core.config import settings

logger = logging.getLogger(__name__)

class ClioService:
    def __init__(self):
        self.client_id = settings.clio_client_id
        self.client_secret = settings.clio_client_secret
        self.redirect_uri = settings.clio_redirect_uri  # Now uses dynamic domain
        self.base_url = settings.clio_base_url
    
    def get_auth_url(self) -> str:
        """Get Clio OAuth authorization URL"""
        return (
            f"{self.base_url}/oauth/authorize"
            f"?client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&response_type=code"
            f"&scope=read write"
        )
    
    async def exchange_code_for_token(self, code: str) -> Dict:
        """Exchange authorization code for access token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/oauth/token",
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.redirect_uri
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Token exchange failed: {response.text}")
    
    async def test_connection(self, db: Session) -> Dict:
        """Test Clio API connection"""
        try:
            token = db.query(ClioToken).first()
            if not token:
                return {"connected": False, "message": "No Clio token found"}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v4/users/who_am_i.json",
                    headers={"Authorization": f"Bearer {token.access_token}"}
                )
                
                if response.status_code == 200:
                    user_data = response.json()
                    return {
                        "connected": True,
                        "message": "Clio connection successful",
                        "user": user_data.get("data", {})
                    }
                else:
                    return {
                        "connected": False,
                        "message": f"API call failed: {response.status_code}"
                    }
        
        except Exception as e:
            logger.error(f"Clio connection test error: {e}")
            return {"connected": False, "message": str(e)}
    
    async def push_time_entries(self, db: Session) -> Dict:
        """Push time entries to Clio"""
        try:
            token = db.query(ClioToken).first()
            if not token:
                return {"success": False, "message": "No Clio token found"}
            
            # Get emails with summaries that haven't been pushed
            emails = db.query(Email).filter(
                Email.summary.isnot(None),
                Email.pushed_to_clio == False
            ).all()
            
            if not emails:
                return {
                    "success": True,
                    "pushed_count": 0,
                    "message": "No summaries to push"
                }
            
            pushed_count = 0
            errors = []
            
            async with httpx.AsyncClient() as client:
                for email in emails:
                    try:
                        # Create time entry data
                        time_entry_data = {
                            "data": {
                                "date": email.date_sent.strftime("%Y-%m-%d") if email.date_sent else None,
                                "quantity": email.billing_hours or 0.25,
                                "price": 0,  # Set appropriate rate
                                "description": email.billing_description or email.summary[:200],
                                "note": email.summary
                            }
                        }
                        
                        # Push to Clio
                        response = await client.post(
                            f"{self.base_url}/api/v4/time_entries.json",
                            headers={"Authorization": f"Bearer {token.access_token}"},
                            json=time_entry_data
                        )
                        
                        if response.status_code in [200, 201]:
                            email.pushed_to_clio = True
                            pushed_count += 1
                        else:
                            errors.append(f"Email {email.id}: {response.text}")
                    
                    except Exception as e:
                        errors.append(f"Email {email.id}: {str(e)}")
            
            db.commit()
            
            return {
                "success": True,
                "pushed_count": pushed_count,
                "errors": errors,
                "message": f"Pushed {pushed_count} time entries to Clio"
            }
        
        except Exception as e:
            logger.error(f"Error pushing time entries: {e}")
            return {"success": False, "message": str(e)}
    
    async def get_matters(self, db: Session) -> List[Dict]:
        """Get matters from Clio"""
        try:
            token = db.query(ClioToken).first()
            if not token:
                raise Exception("No Clio token found")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v4/matters.json",
                    headers={"Authorization": f"Bearer {token.access_token}"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data", [])
                else:
                    raise Exception(f"Failed to fetch matters: {response.text}")
        
        except Exception as e:
            logger.error(f"Error fetching matters: {e}")
            raise
