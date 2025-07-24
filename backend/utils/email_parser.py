import re
from datetime import datetime
from typing import Dict, Optional
import email.utils

def parse_email_date(date_string: str) -> Optional[datetime]:
    """Parse email date string to datetime object"""
    try:
        # Parse RFC 2822 date format
        parsed_date = email.utils.parsedate_tz(date_string)
        if parsed_date:
            timestamp = email.utils.mktime_tz(parsed_date)
            return datetime.fromtimestamp(timestamp)
    except Exception:
        pass
    
    # Fallback to current time
    return datetime.now()

def extract_email_address(email_string: str) -> str:
    """Extract email address from string like 'Name <email@domain.com>'"""
    match = re.search(r'<([^>]+)>', email_string)
    if match:
        return match.group(1)
    
    # If no angle brackets, assume the whole string is the email
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email_string)
    if email_match:
        return email_match.group(0)
    
    return email_string

def clean_email_body(body: str) -> str:
    """Clean email body text"""
    if not body:
        return ""
    
    # Remove excessive whitespace
    body = re.sub(r'\s+', ' ', body)
    
    # Remove common email signatures and footers
    body = re.sub(r'--\s*\n.*', '', body, flags=re.DOTALL)
    body = re.sub(r'Sent from my.*', '', body)
    body = re.sub(r'Get Outlook for.*', '', body)
    
    # Limit length
    return body[:2000].strip()
