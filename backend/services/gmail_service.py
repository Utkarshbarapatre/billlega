import os
import pickle
import base64
from datetime import datetime
from typing import List, Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import logging

logger = logging.getLogger(__name__)

class GmailService:
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    def __init__(self):
        self.service = None
        self.credentials = None
    
    async def authenticate(self) -> Dict:
        """Authenticate with Gmail API"""
        try:
            creds = None
            
            # Load existing credentials
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)
            
            # If no valid credentials, get new ones
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists('client_secret.json'):
                        return {
                            "success": False,
                            "message": "client_secret.json not found. Please download from Google Cloud Console."
                        }
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'client_secret.json', self.SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save credentials
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
            
            self.credentials = creds
            self.service = build('gmail', 'v1', credentials=creds)
            
            return {"success": True, "message": "Gmail authenticated successfully"}
        
        except Exception as e:
            logger.error(f"Gmail authentication error: {e}")
            return {"success": False, "message": str(e)}
    
    async def fetch_emails(
        self,
        start_date: datetime,
        end_date: datetime,
        max_results: int = 100
    ) -> List[Dict]:
        """Fetch emails from Gmail"""
        try:
            if not self.service:
                auth_result = await self.authenticate()
                if not auth_result.get("success"):
                    raise Exception("Gmail authentication failed")
            
            # Build query
            query = f"after:{start_date.strftime('%Y/%m/%d')} before:{end_date.strftime('%Y/%m/%d')}"
            
            # Get message list
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for message in messages:
                try:
                    # Get full message
                    msg = self.service.users().messages().get(
                        userId='me',
                        id=message['id'],
                        format='full'
                    ).execute()
                    
                    # Extract email data
                    email_data = self._extract_email_data(msg)
                    emails.append(email_data)
                
                except Exception as e:
                    logger.error(f"Error processing message {message['id']}: {e}")
                    continue
            
            return emails
        
        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            raise
    
    def _extract_email_data(self, message: Dict) -> Dict:
        """Extract email data from Gmail message"""
        headers = message['payload'].get('headers', [])
        
        # Extract headers
        subject = ""
        sender = ""
        recipient = ""
        date_sent = None
        
        for header in headers:
            name = header['name'].lower()
            value = header['value']
            
            if name == 'subject':
                subject = value
            elif name == 'from':
                sender = value
            elif name == 'to':
                recipient = value
            elif name == 'date':
                try:
                    # Parse date (simplified)
                    date_sent = datetime.now()  # Placeholder
                except:
                    date_sent = datetime.now()
        
        # Extract body
        body = self._extract_body(message['payload'])
        
        return {
            "id": message['id'],
            "thread_id": message['threadId'],
            "subject": subject,
            "sender": sender,
            "recipient": recipient,
            "body": body,
            "date_sent": date_sent
        }
    
    def _extract_body(self, payload: Dict) -> str:
        """Extract email body from payload"""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
                        break
        else:
            if payload['mimeType'] == 'text/plain':
                data = payload['body'].get('data', '')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
        
        return body[:1000]  # Limit body length
