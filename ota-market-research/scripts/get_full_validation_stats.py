import sys
import os
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func

# Add the root directory to sys.path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal
from app.models.ota_property_raw import OTAPropertyRaw
from app.models.ota_validation import OTACoordinateValidation

def get_full_stats():
    db = SessionLocal()
    try:
        # 1. 총 레코드 수
        total_records = db.query(OTAPropertyRaw).count()
        
        # 2. 좌표 보유 수
        coords_count = db.query(OTAPropertyRaw).filter(OTAPropertyRaw.raw_lat.isnot(None)).count()
        
        # 3. 검증된 레코드 수
        validated_records = db.query(OTACoordinateValidation).count()
        
        # 4. 거리별 통계 (이미 검증된 데이터 기준)
        dist_50 = db.query(OTACoordinateValidation).filter(OTACoordinateValidation.nearest_lodging_distance_m <= 50).count()
        dist_100 = db.query(OTACoordinateValidation).filter(OTACoordinateValidation.nearest_lodging_distance_m <= 100).count()
        dist_200 = db.query(OTACoordinateValidation).filter(OTACoordinateValidation.nearest_lodging_distance_m <= 200).count()
        dist_over_200 = db.query(OTACoordinateValidation).filter(OTACoordinateValidation.nearest_lodging_distance_m > 200).count()
        
        # 5. 명칭 불일치 건수
        name_mismatch = db.query(OTACoordinateValidation).filter(OTACoordinateValidation.name_match_status == "mismatch").count()
        
        # 6. status별 건수
        status_counts = db.query(OTACoordinateValidation.existence_validation_status, \
                                 func.count(OTACoordinateValidation.id)).group_by(OTACoordinateValidation.existence_validation_status).all()
        
        print("\n--- [Track B] Full Validation Statistics ---")
        print(f"Total Records: {total_records}")
        print(f"Coordinates Found: {coords_count}")
        print(f"Validated Records: {validated_records}")
        print("-" * 30)
        print(f"Within 50m: {dist_50}")
        print(f"Within 100m: {dist_100}")
        print(f"Within 200m: {dist_200}")
        print(f"Over 200m: {dist_over_200}")
        print(f"Name Mismatches: {name_mismatch}")
        print("-" * 30)
        print("Status Breakdown:")
        for s, c in status_counts:
            print(f" - {s}: {c}")
            
    finally:
        db.close()

if __name__ == "__main__":
    get_full_stats()
