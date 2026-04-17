from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, func
from sqlalchemy.orm import relationship
from ..db import Base

class PropertyAlias(Base):
    __tablename__ = "property_alias"

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("property_master.id"), nullable=True)
    source_name = Column(String, index=True)  # visit_seoul, agoda, booking, etc.
    alias_name = Column(String, index=True)
    alias_address = Column(String)
    alias_lat = Column(Float)
    alias_lng = Column(Float)
    alias_url = Column(String)
    
    match_confidence = Column(Float)  # 0.0 to 1.0 or 0 to 100
    is_verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    property = relationship("PropertyMaster", backref="aliases")
