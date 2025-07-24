from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import os

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./legal_billing.db")

# Create engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class
Base = declarative_base()

class ClioToken(Base):
    __tablename__ = "clio_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    """Initialize database tables"""
    from ..models.email import Base as EmailBase
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    EmailBase.metadata.create_all(bind=engine)
