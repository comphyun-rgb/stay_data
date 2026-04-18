from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func
from .ota_property_raw import Base

class OTARoomOfferRaw(Base):
    """
    OTA 숙소 내의 구체적인 객실(Room) 및 상품(Offer/Rate Plan) 정보.
    숙소(Property) 레벨보다 더 세부적인 분석을 가능하게 함.
    """
    __tablename__ = "ota_room_offer_raw"

    id = Column(Integer, primary_key=True, index=True)
    property_raw_id = Column(Integer, ForeignKey("ota_property_raw.id"), index=True, nullable=False)
    
    # [Offer Info]
    ota_source = Column(String, index=True)
    room_type_name = Column(String, index=True) # 원문 객실명
    room_type_std = Column(String, index=True) # 표준화된 객실 타입 (dorm_bed, private_room 등)
    rate_plan_name = Column(String) # 요금제 명칭
    
    # [Capacity & Bedding]
    max_guests = Column(Integer)
    bed_count = Column(Integer)
    bed_type_raw = Column(String) # '1 Double Bed', '2 Bunk Beds' 등 원문
    
    # [Bathroom]
    private_bathroom_yn = Column(String) # Y / N
    bathroom_type = Column(String) # private, shared, unknown
    
    # [Policies & Features]
    cancel_policy_raw = Column(String)
    refundable_yn = Column(String) # Y / N
    breakfast_yn = Column(String) # Y / N
    tax_included_yn = Column(String) # Y / N
    
    # [Financial Info]
    price_total_krw = Column(Float)
    price_per_night_krw = Column(Float)
    currency = Column(String, default="KRW")
    
    # [Status]
    availability_status = Column(String, default="available")
    raw_offer_id = Column(String, index=True) # OTA 내부 상품 고유 ID
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
