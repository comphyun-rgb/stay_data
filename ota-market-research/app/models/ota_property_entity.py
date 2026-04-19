from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func, Boolean
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
    특정 날짜/조건으로 관측된 판매 상태와 가격 스냅샷 (시계열).
    매진 상태와 수집 성공 여부를 정밀하게 기록함.
    """
    __tablename__ = "ota_snapshot"

    id = Column(Integer, primary_key=True, index=True)
    
    # [References]
    property_raw_id = Column(Integer, ForeignKey("ota_property_raw.id"), index=True)
    room_offer_raw_id = Column(Integer, ForeignKey("ota_room_offer_raw.id"), index=True)
    ota_source = Column(String, index=True)
    
    # [Time Info]
    collected_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    search_date = Column(String, index=True) # 수집 기준 날짜 (YYYY-MM-DD)
    checkin_date = Column(String, index=True) # 투숙 예정일
    nights = Column(Integer, default=1)
    guests = Column(Integer, default=2)
    
    # [Availability & Status]
    scrape_success_yn = Column(Boolean, default=True) # 수집 자체 성공 여부
    observed_price_yn = Column(Boolean, default=True) # 가격 노출 여부
    sold_out_yn = Column(Boolean, default=False) # 매진 여부
    bookable_yn = Column(Boolean, default=True) # 실제 예약 가능 상태 여부
    
    availability_text_raw = Column(String) # OTA 화면상 원문 (예: 'Sold out', '예약마감')
    inventory_hint_text_raw = Column(String) # 수량 힌트 (예: '마지막 1개 남음')
    search_rank = Column(Integer) # 검색 순위
    
    # [Price Data]
    price_total_krw = Column(Float)
    price_per_night_krw = Column(Float)
    taxes_and_fees_included_yn = Column(String, default="Y")
    currency = Column(String, default="KRW")
    
    rating = Column(Float) # 해당 시점의 평점
    review_count = Column(Integer) # 해당 시점의 리뷰 수
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
