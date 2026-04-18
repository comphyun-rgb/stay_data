from sqlalchemy import Column, Integer, String, Float, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class OTAPropertyRaw(Base):
    """
    OTA(Agoda, Booking, Airbnb) 검색 결과 리스트에서 수집된 원시 데이터 테이블.
    이후 정합성 과정을 거쳐 ota_property_entity로 통합됨.
    """
    __tablename__ = "ota_property_raw"

    id = Column(Integer, primary_key=True, index=True)
    
    # [Search Info]
    ota_source = Column(String, index=True, nullable=False) # agoda, booking_com, airbnb
    search_area = Column(String, index=True) # e.g., 'hongdae'
    search_keyword = Column(String, index=True)
    collected_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # [Booking Info]
    checkin_date = Column(String, index=True)
    nights = Column(Integer, default=1)
    guests = Column(Integer, default=2)
    
    # [Listing Info]
    raw_listing_name = Column(String, index=True)
    raw_listing_url = Column(String, unique=True)
    raw_listing_id = Column(String, index=True) # OTA 내부 고유 ID
    raw_address = Column(String)
    raw_lat = Column(Float)
    raw_lng = Column(Float)
    
    # [Categorization]
    property_type_raw = Column(String) # e.g., 'Hotel', 'Apartment'
    property_type_std = Column(String, index=True) # e.g., 'hotel', 'guesthouse', 'hostel'
    star_rating = Column(Float)
    
    # [Financial Info]
    price_total_krw = Column(Float)
    price_per_night_krw = Column(Float)
    currency = Column(String, default="KRW")
    
    # [Reputation & Status]
    rating = Column(Float)
    review_count = Column(Integer)
    availability_status = Column(String, default="available") # available / sold_out
    
    # [Features]
    breakfast_yn = Column(String) # Y / N / NULL
    refundable_yn = Column(String) # Y / N / NULL
    
    # [Operational Metadata]
    source_rank = Column(Integer) # 검색 결과 내 순위
    page_no = Column(Integer) # 수집된 검색 페이지 번호
    note = Column(String)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
