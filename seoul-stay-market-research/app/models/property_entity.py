from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func
from ..db import Base

class PropertyEntity(Base):
    """
    중복된 PropertyMaster 레코드들을 하나로 통합한 실제 숙소 엔티티.
    OTA 조사 및 최종 시장 데이터 분석의 기준점이 됨.
    """
    __tablename__ = "property_entity"

    id = Column(Integer, primary_key=True, index=True)
    display_name = Column(String, index=True, nullable=False)
    representative_address = Column(String)
    district = Column(String, index=True)
    cluster_area = Column(String, index=True)
    
    # 대표 좌표
    lat = Column(Float)
    lng = Column(Float)
    
    # 엔티티에 속한 마스터 레코드 수 (참조용)
    master_count = Column(Integer, default=1)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
