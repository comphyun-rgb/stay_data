from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path

# DB 파일 경로 설정
DB_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DB_DIR / "ota_market.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# Ensure directory exists
DB_DIR.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    from .models.ota_property_raw import Base
    from .models.ota_room_offer_raw import OTARoomOfferRaw
    from .models.ota_property_entity import OTAPropertyEntity, OTASnapshot
    from .models.ota_validation import OTACoordinateValidation
    from .models.ota_mapping import OTAManualMatch
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print(f"Track B Database initialized at: {DB_PATH}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
