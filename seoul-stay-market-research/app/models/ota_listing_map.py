from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func, UniqueConstraint
from ..db import Base

class OTAMapping(Base):
    """
    PropertyEntity와 실제 OTA(Booking, Agoda 등) 상의 Listing을 연결하는 매핑 테이블.
    하나의 숙소 엔티티는 소스별로 여러 개의 리스팅을 가질 수 있음.
    """
    __tablename__ = "ota_listing_map"

    id = Column(Integer, primary_key=True, index=True)
    property_entity_id = Column(Integer, ForeignKey("property_entity.id"), index=True)
    
    ota_source = Column(String, index=True) # booking_com, agoda, airbnb 등
    
    # [OTA 정보]
    raw_listing_name = Column(String)
    raw_listing_url = Column(String, index=True) # 고유 식별자로 활용
    raw_address = Column(String)
    raw_lat = Column(Float)
    raw_lng = Column(Float)
    
    # [매칭 상태 및 품질]
    # status: matched, review_needed, rejected, unmapped
    match_status = Column(String, default="matched", index=True)
    match_confidence = Column(Float, default=1.0)
    
    # [검수 정보]
    verified_by = Column(String)
    verified_at = Column(DateTime)
    note = Column(String)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 동일 소스 내에서 URL 중복 방지 (데이터 무결성)
    __table_args__ = (
        UniqueConstraint('ota_source', 'raw_listing_url', name='_ota_url_uc'),
    )
