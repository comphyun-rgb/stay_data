import sys
import os
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import desc

# Add the root directory to sys.path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal
from app.models.ota_property_raw import OTAPropertyRaw
from app.models.ota_validation import OTACoordinateValidation
from app.models.ota_mapping import OTAManualMatch

def select_manual_targets(limit=50):
    db = SessionLocal()
    try:
        # Join OTAPropertyRaw and OTACoordinateValidation
        targets = db.query(OTAPropertyRaw, OTACoordinateValidation)\
            .join(OTACoordinateValidation, OTAPropertyRaw.id == OTACoordinateValidation.property_raw_id)\
            .filter(OTACoordinateValidation.existence_validation_status == 'probable_match')\
            .order_by(desc(OTAPropertyRaw.review_count))\
            .limit(limit).all()
        
        print(f"Selected {len(targets)} manual review candidates.")
        
        new_count = 0
        seen_urls = set()
        
        for prop, val in targets:
            if prop.raw_listing_url in seen_urls: continue
            seen_urls.add(prop.raw_listing_url)

            # Check if already in manual mapping
            exists = db.query(OTAManualMatch).filter_by(raw_listing_url=prop.raw_listing_url).first()
            if not exists:
                new_map = OTAManualMatch(
                    ota_source=prop.ota_source,
                    raw_listing_name=prop.raw_listing_name,
                    raw_listing_url=prop.raw_listing_url,
                    raw_address=prop.raw_address,
                    mapping_status="pending",
                    note=f"Auto-selected (Reviews: {prop.review_count}, Dist: {val.nearest_lodging_distance_m:.1f}m)"
                )
                db.add(new_map)
                new_count += 1
        
        db.commit()
        print(f"Added {new_count} new records to ota_manual_match.")
    finally:
        db.close()

def generate_operational_report():
    db = SessionLocal()
    try:
        total = db.query(OTAPropertyRaw).count()
        auto_matched = db.query(OTACoordinateValidation).filter(OTACoordinateValidation.existence_validation_status.like('same_property%')).count()
        probable = db.query(OTACoordinateValidation).filter_by(existence_validation_status='probable_match').count()
        addr_missing = db.query(OTAPropertyRaw).filter(OTAPropertyRaw.raw_address == None).count()
        url_missing = db.query(OTAPropertyRaw).filter(OTAPropertyRaw.raw_listing_url == None).count()
        manual_pending = db.query(OTAManualMatch).filter_by(mapping_status='pending').count()

        print("\n### OTA 운영 리포트 (Operational Report)")
        print(f"- **총 리스팅 수**: {total}")
        print(f"- **자동 매칭 완료 (High/Med Confidence)**: {auto_matched}")
        print(f"- **매칭 확률 높음 (Probable Match)**: {probable}")
        print(f"- **수동 검토 대기 (Manual Review Targets)**: {manual_pending}")
        print(f"- **주소 누락 (Address Missing)**: {addr_missing}")
        print(f"- **URL 누락 (URL Missing)**: {url_missing}")
        
    finally:
        db.close()

if __name__ == "__main__":
    select_manual_targets()
    generate_operational_report()
