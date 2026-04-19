from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class OTAPropertyRaw(Base):
    """
    OTA(Agoda, Booking, Airbnb) 숙소 레벨 원시 데이터.
    숙소 자체의 수준, 위치, 시설 정보를 저장함.
    """
    __tablename__ = "ota_property_raw"

    id = Column(Integer, primary_key=True, index=True)
    
    # [0. Internal Link]
    entity_id = Column(Integer, ForeignKey("ota_property_entity.id"), index=True)
    
    # [1. Search & Source Info]
    ota_source = Column(String, index=True, nullable=False) # agoda, booking_com, airbnb
    source_role = Column(String, index=True) # primary (Booking), secondary (Agoda), area_reference (Airbnb)
    raw_listing_name = Column(String, index=True)
    raw_listing_url = Column(String, unique=True)
    raw_listing_id = Column(String, index=True)
    collected_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # [2. Location & Precision]
    raw_address = Column(String)
    raw_lat = Column(Float)
    raw_lng = Column(Float)
    geo_precision = Column(String, default="exact") # exact, nearby, approximate_area, hidden
    area_cluster = Column(String, index=True) # e.g., 'hongdae_main', 'yeonnam_dist'
    approx_lat = Column(Float) # For Airbnb
    approx_lng = Column(Float) # For Airbnb
    region_code = Column(String, index=True) # e.g., 'hongdae'
    region_label = Column(String) # e.g., '홍대/연남'
    sub_area = Column(String) # e.g., 'yeonnam'
    cluster_area = Column(String)
    nearest_station_name = Column(String)
    station_distance_m = Column(Float)
    central_point_distance_m = Column(Float)
    
    # [3. Official Grade & Type]
    property_type_raw = Column(String) # 원문 유형
    property_type_std = Column(String, index=True) # hotel, guesthouse, hostel, apartment, etc.
    official_star_rating = Column(Float) # OTA star rating or official grade
    
    # [4. Internal Grade System (Scoring)]
    location_score = Column(Float, default=0) # Max 25
    facility_score = Column(Float, default=0) # Max 30
    review_score_component = Column(Float, default=0) # Max 25
    scale_score = Column(Float, default=0) # Max 20
    total_grade_score = Column(Float, default=0, index=True) # Max 100
    
    internal_grade = Column(String, index=True) # Premium, Upper-mid, Standard, Budget
    grade_reason_note = Column(String) # 등급 산정 근거 요약
    
    # [5. Reputation]
    review_score_raw = Column(Float) # OTA 원문 평점
    review_score_std = Column(Float) # 10점 만점 기준 변환 평점
    review_count = Column(Integer)
    
    # [6. Facilities & Policy (Summary)]
    facility_text_raw = Column(String)
    checkin_policy_text_raw = Column(String)
    
    # [7. Facilities (Standardized Flags)]
    private_bathroom_yn = Column(String) # Y / N / NULL
    bathroom_type = Column(String) # private, shared, mixed, unknown
    elevator_yn = Column(String) # Y / N / NULL
    parking_yn = Column(String)
    breakfast_yn = Column(String)
    kitchen_yn = Column(String)
    laundry_yn = Column(String)
    wifi_yn = Column(String)
    aircon_yn = Column(String)
    heating_yn = Column(String)
    
    # [8. Current Status Info]
    sold_out_flag_latest = Column(Boolean, default=False)
    availability_text_latest = Column(String)
    search_rank_latest = Column(Integer)
    
    # [9. Operational Metadata]
    note = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
