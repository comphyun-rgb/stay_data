from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func
from .ota_property_raw import Base

class OTARoomOfferRaw(Base):
    """
    OTA 객실/상품 레벨 데이터.
    실제로 판매되는 객실의 조건과 구성을 저장함.
    """
    __tablename__ = "ota_room_offer_raw"

    id = Column(Integer, primary_key=True, index=True)
    property_raw_id = Column(Integer, ForeignKey("ota_property_raw.id"), index=True, nullable=False)
    
    # [1. Offer Source]
    ota_source = Column(String, index=True)
    room_type_name = Column(String, index=True) # 원문 객실명
    
    # [2. Classification]
    room_type_std = Column(String, index=True) # dorm_bed, private_room, hotel_room, family_room, studio, apartment
    room_analysis_type = Column(String, index=True) # dorm_1p, double_2p, family_4p, other
    rate_plan_name = Column(String) # 요금제 명칭 (e.g., 'Non-refundable Saver')
    
    # [3. Capacity & Bedding]
    max_guests = Column(Integer)
    min_guests = Column(Integer, default=1)
    bed_count = Column(Integer)
    bed_type_raw = Column(String) # '1 Double Bed', '2 Bunk Beds'
    room_size_m2 = Column(Float) # 객실 면적
    
    # [4. Bathroom]
    private_bathroom_yn = Column(String) # Y / N
    bathroom_type = Column(String) # private, shared, mixed, unknown
    
    # [5. Amenities & Features]
    breakfast_yn = Column(String) # Y / N
    refundable_yn = Column(String) # Y / N
    tax_included_yn = Column(String) # Y / N
    cancel_policy_raw = Column(String)
    amenities_room_raw = Column(String) # 객실별 편의시설 원문
    
    window_yn = Column(String) # 창문 유무
    smoke_free_yn = Column(String) # 금연실 여부
    
    # [6. Current Snapshot Data (Denormalized for quick access)]
    price_total_krw = Column(Float)
    price_per_night_krw = Column(Float)
    currency = Column(String, default="KRW")
    availability_status = Column(String, default="available")
    raw_offer_id = Column(String, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
