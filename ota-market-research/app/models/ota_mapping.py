from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from .ota_property_raw import Base

class OTAManualMatch(Base):
    """
    자동 매칭이 어려운 OTA 리스팅과 마스터 데이터 간의 수동 매핑 테이블.
    """
    __tablename__ = "ota_manual_match"

    id = Column(Integer, primary_key=True, index=True)
    
    # [Source Info]
    ota_source = Column(String, index=True)
    raw_listing_name = Column(String)
    raw_listing_url = Column(String, unique=True)
    raw_address = Column(String)
    
    # [Target Master Info (Track A)]
    matched_master_id = Column(Integer, index=True) # property_master_full.csv의 id
    matched_master_name = Column(String)
    
    # [Operational Status]
    # mapping_status: pending, matched, unmatched, ignored
    mapping_status = Column(String, index=True, default="pending")
    
    verified_by = Column(String)
    verified_at = Column(DateTime(timezone=True))
    note = Column(String)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
