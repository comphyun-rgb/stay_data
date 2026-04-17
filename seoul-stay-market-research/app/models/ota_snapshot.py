from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func
from ..db import Base

class OTASnapshot(Base):
    """
    특정 리스팅(Listing)에 대한 시점별 가격, 평점, 상태 스냅샷.
    """
    __tablename__ = "ota_snapshot"

    id = Column(Integer, primary_key=True, index=True)
    
    # [Foreign Keys]
    # 매핑 테이블과의 연결을 최우선으로 함
    ota_listing_map_id = Column(Integer, ForeignKey("ota_listing_map.id"), index=True)
    property_entity_id = Column(Integer, ForeignKey("property_entity.id"), index=True)
    
    # [Metadata]
    collected_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    ota_source = Column(String, index=True)
    
    # [Booking Conditions]
    checkin_date = Column(String, index=True) # YYYY-MM-DD
    nights = Column(Integer, default=1)
    guests = Column(Integer, default=2)
    room_type = Column(String) # e.g., 'Double Room', 'Deluxe Twin'
    
    # [Policy & Includes]
    refundable_yn = Column(String) # Y / N / NULL
    breakfast_yn = Column(String)  # Y / N / NULL
    
    # [Price Data]
    price_total_krw = Column(Float)
    price_per_night_krw = Column(Float)
    
    # [Reputation & Availability]
    rating = Column(Float)
    review_count = Column(Integer)
    availability_status = Column(String, default="available") # available, sold_out
    
    # [Extended Info]
    raw_listing_name = Column(String)
    raw_listing_url = Column(String)
    note = Column(String)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
