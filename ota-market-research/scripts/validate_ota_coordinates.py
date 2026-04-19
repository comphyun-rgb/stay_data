import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime
from sqlalchemy.orm import Session

# Add the root directory to sys.path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal
from app.models.ota_property_raw import OTAPropertyRaw
from app.models.ota_validation import OTACoordinateValidation

# Track A Master Data Path
MASTER_DATA_PATH = r"c:\stay_data\stay_data\seoul-stay-market-research\data\exports\property_master_full.csv"

def calculate_distance_vectorized(lat1, lon1, lat2, lon2):
    R = 6371000
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c

class OTAValidator:
    def __init__(self, master_path):
        print(f"Loading Track A Master Data from: {master_path}")
        self.master_df = pd.read_csv(master_path)
        self.master_df = self.master_df.dropna(subset=['lat', 'lng'])
        print(f"Loaded {len(self.master_df)} valid master records.")

    def find_nearest_lodging(self, raw_lat, raw_lng):
        if pd.isna(raw_lat) or pd.isna(raw_lng):
            return None, 999999.0
        distances = calculate_distance_vectorized(
            raw_lat, raw_lng, 
            self.master_df['lat'].values, self.master_df['lng'].values
        )
        min_idx = np.argmin(distances)
        nearest = self.master_df.iloc[min_idx]
        return nearest, distances[min_idx]

    def validate_record(self, db: Session, raw_prop: OTAPropertyRaw):
        raw_lat = raw_prop.raw_lat
        raw_lng = raw_prop.raw_lng
        raw_name = raw_prop.raw_listing_name
        raw_addr = raw_prop.raw_address or ""

        nearest_item, distance = self.find_nearest_lodging(raw_lat, raw_lng)
        if nearest_item is None: return None

        nearest_name = nearest_item['canonical_name']
        name_match = "mismatch"
        if raw_name and nearest_name:
            s1 = str(raw_name).lower().replace(" ", "")
            s2 = str(nearest_name).lower().replace(" ", "")
            if s1 == s2: name_match = "exact_match"
            elif s1 in s2 or s2 in s1: name_match = "similar"

        addr_match = "no_address"
        if raw_addr: addr_match = "review_needed"

        status = "review_needed"
        note = f"Track A Master ({nearest_name})와의 거리: {distance:.1f}m"
        
        if distance <= 50 and name_match in ["exact_match", "similar"]:
            status = "confirmed_exact"
        elif distance <= 100:
            status = "confirmed_nearby"
        elif distance <= 200:
            status = "probable_match"
        elif distance > 200:
            status = "invalid_suspected"
            note += " | 반경 200m 내 일치하는 숙소 없음."

        val = OTACoordinateValidation(
            property_raw_id=raw_prop.id,
            ota_source=raw_prop.ota_source,
            raw_listing_name=raw_name,
            raw_listing_id=raw_prop.raw_listing_id,
            raw_lat=raw_lat,
            raw_lng=raw_lng,
            nearest_lodging_name=nearest_name,
            nearest_lodging_distance_m=float(distance),
            name_match_status=name_match,
            address_match_status=addr_match,
            existence_validation_status=status,
            existence_validation_note=note,
            validated_at=datetime.now()
        )
        db.add(val)
        return val

def run_actual_validation(limit=20):
    db = SessionLocal()
    validator = OTAValidator(MASTER_DATA_PATH)
    results_data = []
    try:
        targets = db.query(OTAPropertyRaw).filter(OTAPropertyRaw.raw_lat.isnot(None)).limit(limit).all()
        for t in targets:
            res = validator.validate_record(db, t)
            if res:
                # Convert to dict to avoid DetachedInstanceError
                results_data.append({
                    "ota_source": res.ota_source,
                    "raw_listing_name": res.raw_listing_name,
                    "raw_lat": res.raw_lat,
                    "raw_lng": res.raw_lng,
                    "nearest_lodging_name": res.nearest_lodging_name,
                    "nearest_lodging_distance_m": res.nearest_lodging_distance_m,
                    "name_match_status": res.name_match_status,
                    "existence_validation_status": res.existence_validation_status,
                    "existence_validation_note": res.existence_validation_note
                })
        db.commit()
        return results_data
    finally:
        db.close()

if __name__ == "__main__":
    run_actual_validation()
