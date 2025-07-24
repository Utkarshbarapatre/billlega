import os
import pickle
from typing import Optional, Dict
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import logging

logger = logging.getLogger(__name__)

class AuthService:
    """Handle authentication for various services"""
    
    GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    def __init__(self):
        self.credentials_file = os.getenv("GOOGLE_CLIENT_SECRET_FILE", "client_secret.json")
        self.token_file = "token.pickle"
    
    def get_gmail_credentials(self) -> Optional[Credentials]:
        """Get Gmail API credentials"""
        try:
            creds = None
            
            # Load existing credentials
            if os.path.exists(self.token_file):
                with open(self.token_file, 'rb') as token:
                    creds = pickle.load(token)
            
            # If no valid credentials, get new ones
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_file):
                        logger.error(f"Credentials file not found: {self.credentials_file}")
                        return None
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, self.GMAIL_SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save credentials
                with open(self.token_file, 'wb') as token:
                    pickle.dump(creds, token)
            
            return creds
        
        except Exception as e:
            logger.error(f"Error getting Gmail credentials: {e}")
            return None
    
    def is_gmail_authenticated(self) -> bool:
        """Check if Gmail is authenticated"""
        creds = self.get_gmail_credentials()
        return creds is not None and creds.valid
