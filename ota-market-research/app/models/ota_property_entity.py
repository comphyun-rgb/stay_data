from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func
from .ota_property_raw import Base

class OTAPropertyEntity(Base):
    """
    여러 OTA에 흩어진 동일 숙소를 하나로 묶는 가상 매칭 엔티티.
    (Track B 내부의 정합성용 모델)
    """
    __tablename__ = "ota_property_entity"

    id = Column(Integer, primary_key=True, index=True)
    canonical_name = Column(String, index=True)
    representative_address = Column(String)
    lat = Column(Float)
    lng = Column(Float)
    
    # [Operational Metadata]
    note = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class OTASnapshot(Base):
    """
    특정 리스팅(Listing)에 대한 시점별 가격, 평점, 가용성 스냅샷 (시계열 데이터).
    """
    __tablename__ = "ota_snapshot"

    id = Column(Integer, primary_key=True, index=True)
    
    # [Reference]
    property_raw_id = Column(Integer, ForeignKey("ota_property_raw.id"), index=True)
    room_offer_raw_id = Column(Integer, ForeignKey("ota_room_offer_raw.id"), index=True)
    ota_property_entity_id = Column(Integer, ForeignKey("ota_property_entity.id"), index=True)
    
    # [Offer Context]
    room_type_name = Column(String) # 스냅샷 시점의 객실명 기록
    
    # [Capture Metadata]
    collected_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    ota_source = Column(String, index=True)
    
    # [Point-in-Price Data]
    checkin_date = Column(String, index=True)
    price_total_krw = Column(Float)
    price_per_night_krw = Column(Float)
    rating = Column(Float)
    review_count = Column(Integer)
    availability_status = Column(String) # available, sold_out
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
