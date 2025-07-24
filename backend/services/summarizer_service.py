import os
import openai
from typing import Dict, List
from sqlalchemy.orm import Session
import logging

from ..models.email import Email

logger = logging.getLogger(__name__)

class SummarizerService:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    async def generate_summaries(self, db: Session) -> Dict:
        """Generate AI summaries for emails without summaries"""
        try:
            # Get emails without summaries
            emails = db.query(Email).filter(Email.summary.is_(None)).all()
            
            if not emails:
                return {
                    "success": True,
                    "summaries_generated": 0,
                    "message": "No emails need summaries"
                }
            
            summaries_generated = 0
            errors = []
            
            for email in emails:
                try:
                    # Generate summary
                    summary_data = await self._generate_single_summary(email)
                    
                    # Update email with summary
                    email.summary = summary_data["summary"]
                    email.billing_hours = summary_data["billing_hours"]
                    email.billing_description = summary_data["billing_description"]
                    
                    summaries_generated += 1
                
                except Exception as e:
                    logger.error(f"Error generating summary for email {email.id}: {e}")
                    errors.append(f"Email {email.id}: {str(e)}")
            
            db.commit()
            
            return {
                "success": True,
                "summaries_generated": summaries_generated,
                "errors": errors,
                "message": f"Generated {summaries_generated} summaries"
            }
        
        except Exception as e:
            logger.error(f"Error in batch summary generation: {e}")
            return {"success": False, "message": str(e)}
    
    async def _generate_single_summary(self, email: Email) -> Dict:
        """Generate summary for a single email"""
        try:
            # Prepare prompt
            prompt = f"""
            Please analyze this legal email and provide:
            1. A professional summary suitable for legal billing
            2. Suggested billing hours (in decimal format, e.g., 0.25, 0.5, 1.0)
            3. A brief billing description

            Email Details:
            Subject: {email.subject}
            From: {email.sender}
            To: {email.recipient}
            Date: {email.date_sent}
            
            Email Content:
            {email.body[:2000]}  # Limit content length
            
            Please respond in JSON format:
            {{
                "summary": "Professional summary of the email content and legal significance",
                "billing_hours": 0.25,
                "billing_description": "Brief description for billing purposes"
            }}
            """
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a legal assistant helping with email summarization for billing purposes. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            # Parse response
            content = response.choices[0].message.content.strip()
            
            # Try to parse JSON response
            import json
            try:
                summary_data = json.loads(content)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                summary_data = {
                    "summary": content[:300],
                    "billing_hours": 0.25,
                    "billing_description": f"Email communication regarding {email.subject[:50]}"
                }
            
            return summary_data
        
        except Exception as e:
            logger.error(f"Error generating single summary: {e}")
            # Return default summary
            return {
                "summary": f"Email communication from {email.sender} regarding {email.subject}",
                "billing_hours": 0.25,
                "billing_description": f"Email review and response - {email.subject[:50]}"
            }
