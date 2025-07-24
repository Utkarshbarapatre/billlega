from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Email(Base):
    __tablename__ = "emails"
    
    id = Column(Integer, primary_key=True, index=True)
    gmail_id = Column(String, unique=True, index=True)
    thread_id = Column(String)
    subject = Column(String)
    sender = Column(String)
    recipient = Column(String)
    body = Column(Text)
    date_sent = Column(DateTime)
    summary = Column(Text, nullable=True)
    billing_hours = Column(Float, nullable=True)
    billing_description = Column(Text, nullable=True)
    pushed_to_clio = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
