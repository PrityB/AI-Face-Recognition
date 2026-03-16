from sqlalchemy import Column, Integer, String, Float, Boolean, JSON, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_identifier = Column(String, unique=True, index=True, nullable=False)
    kyc_status = Column(String, default="PENDING") # PENDING, APPROVED, REJECTED
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    verifications = relationship("Verification", back_populates="user")
    
class Verification(Base):
    __tablename__ = "verifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Results
    is_live = Column(Boolean, nullable=True)
    liveness_score = Column(Float, nullable=True)
    face_match = Column(Boolean, nullable=True)
    face_confidence = Column(Float, nullable=True)
    
    # Document Info
    doc_type = Column(String, nullable=True)
    doc_data = Column(JSON, nullable=True)
    
    # Risk Profile
    risk_score = Column(Float, nullable=True)
    risk_level = Column(String, nullable=True) # LOW, MEDIUM, HIGH, CRITICAL
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("User", back_populates="verifications")
