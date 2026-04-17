from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import SQLALCHEMY_DATABASE_URL
import os
from pathlib import Path

# Create database engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def init_db():
    """
    Initialize the database, creating all tables.
    """
    # Ensure data directory exists
    db_relative_path = SQLALCHEMY_DATABASE_URL.replace("sqlite:///", "")
    Path(db_relative_path).parent.mkdir(parents=True, exist_ok=True)
    
    # [IMPORTANT] 임포트해야 metadata.create_all() 시 테이블이 생성됩니다.
    from .models.property_master import PropertyMaster
    from .models.property_alias import PropertyAlias
    from .models.property_entity import PropertyEntity
    from .models.ota_snapshot import OTASnapshot
    from .models.ota_listing_map import OTAMapping # 파일럿 연구용 매핑 테이블 추가
    
    Base.metadata.create_all(bind=engine)
    print(f"Database initialized at: {db_relative_path}")

def get_db():
    """
    Dependency to get a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
