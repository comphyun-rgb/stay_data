from sqlalchemy import Column, Integer, String, Float, Date, func
from ..db import Base

class AreaSummary(Base):
    __tablename__ = "area_summary"

    id = Column(Integer, primary_key=True, index=True)
    summary_date = Column(Date, index=True)
    cluster_area = Column(String, index=True)
    property_type_std = Column(String, index=True)
    ota_source = Column(String, index=True)
    
    sample_count = Column(Integer)
    min_price = Column(Float)
    median_price = Column(Float)
    avg_price = Column(Float)
    max_price = Column(Float)
    avg_rating = Column(Float)
