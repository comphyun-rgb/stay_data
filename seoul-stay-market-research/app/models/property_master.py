import math
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func, text
from ..db import Base

class PropertyMaster(Base):
    __tablename__ = "property_master"

    id = Column(Integer, primary_key=True, index=True)
    entity_id = Column(Integer, ForeignKey("property_entity.id"), index=True)
    
    canonical_name = Column(String, index=True, nullable=False)
    property_type_std = Column(String)
    
    # [Borough & Zone Info]
    district_normalized = Column(String, index=True)
    cluster_area = Column(String, index=True)
    hongdae_zone = Column(String, index=True) # 신규: core_hongdae, hongdae_area, fringe_hongdae
    
    address_road = Column(String)
    lat = Column(Float)
    lng = Column(Float)
    
    status_std = Column(String, default="unknown")
    
    # [Basic Detail]
    phone = Column(String)
    room_count = Column(Integer)
    license_date = Column(String)
    
    # [Raw Info]
    property_type_raw = Column(String)
    raw_status = Column(String)
    raw_status_detail = Column(String)
    district = Column(String)
    raw_x = Column(String)
    raw_y = Column(String)
    raw_data_json = Column(String)
    source_priority = Column(String)
    name_eng = Column(String)
    floors_above = Column(Integer)
    floors_below = Column(Integer)
    building_area = Column(Float)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
