from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func
from .ota_property_raw import Base

class OTACoordinateValidation(Base):
    """
    OTA 원시 좌표(raw_lat, raw_lng)의 실제 숙박업소 존재 여부 검증 결과 테이블.
    """
    __tablename__ = "ota_coordinate_validation"

    id = Column(Integer, primary_key=True, index=True)
    
    # [References]
    property_raw_id = Column(Integer, ForeignKey("ota_property_raw.id"), index=True)
    
    # [Raw Data Snapshot for Reference]
    ota_source = Column(String, index=True)
    raw_listing_name = Column(String)
    raw_listing_id = Column(String)
    raw_lat = Column(Float)
    raw_lng = Column(Float)
    
    # [Validation Results]
    nearest_lodging_name = Column(String) # 지도/마스터 데이터 기준 가장 가까운 숙소명
    nearest_lodging_distance_m = Column(Float) # 실제 숙소와의 거리 (미터)
    
    # [Status Codes]
    # 명칭 대조: exact_match, similar, mismatch
    name_match_status = Column(String)
    # 주소 대조: match, mismatch, no_address
    address_match_status = Column(String)
    
    # [Existence Decision]
    # confirmed_exact, confirmed_nearby, probable_match, review_needed, invalid_suspected
    existence_validation_status = Column(String, index=True)
    existence_validation_note = Column(String)
    
    validated_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
