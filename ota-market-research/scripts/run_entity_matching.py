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
from app.utils.matcher import normalize_name, calculate_name_similarity, get_similarity_level, normalize_address

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

class EntityMatcher:
    def __init__(self, master_path):
        print(f"Loading Master Data: {master_path}")
        self.master_df = pd.read_csv(master_path)
        self.master_df = self.master_df.dropna(subset=['lat', 'lng'])

    def match_record(self, db: Session, raw_prop: OTAPropertyRaw):
        raw_lat = raw_prop.raw_lat
        raw_lng = raw_prop.raw_lng
        if pd.isna(raw_lat) or pd.isna(raw_lng): return None

        # 1. Calculate distances to ALL master records
        distances = calculate_distance_vectorized(
            raw_lat, raw_lng, 
            self.master_df['lat'].values, self.master_df['lng'].values
        )
        
        # 2. Get Top 200 Nearest Candidates (Safe for dense areas)
        top_indices = np.argsort(distances)[:200]
        candidates = self.master_df.iloc[top_indices].copy()
        candidates['distance'] = distances[top_indices]

        # 3. Evaluate each candidate and pick the BEST match
        best_candidate = None
        max_confidence_score = -1

        for _, cand in candidates.iterrows():
            # Calculate Similarity Scores
            name_score = calculate_name_similarity(raw_prop.raw_listing_name, cand['canonical_name'])
            name_sim_level = get_similarity_level(name_score)
            
            # Address Match
            addr_data_t = normalize_address(raw_prop.raw_address)
            addr_data_c = normalize_address(cand['address_road'])
            
            addr_match = "no_address"
            if addr_data_t['street'] and addr_data_c['street']:
                addr_match = "mismatch"
                if addr_data_t['street'] == addr_data_c['street']:
                    addr_match = "exact_match"
                elif addr_data_t['dong'] == addr_data_c['dong'] and addr_data_t['dong'] != "":
                    addr_match = "dong_match"

            # Confidence Scoring
            conf_score = 0
            if cand['distance'] <= 50: conf_score += 40
            elif cand['distance'] <= 150: conf_score += 20
            elif cand['distance'] <= 300: conf_score += 10
            
            if name_sim_level == "exact": conf_score += 60
            elif name_sim_level == "high": conf_score += 40
            
            if addr_match == "exact_match": conf_score += 100 # Address is the strongest signal
            
            if conf_score > max_confidence_score:
                max_confidence_score = conf_score
                best_candidate = {
                    "cand": cand,
                    "distance": cand['distance'],
                    "name_sim": name_sim_level,
                    "addr_match": addr_match,
                    "conf_score": conf_score
                }

        # 4. Determine Final Status
        final_status = "nearby_but_unmatched"
        if best_candidate['conf_score'] >= 100:
            final_status = "same_property_high_confidence"
        elif best_candidate['conf_score'] >= 60:
            final_status = "same_property_medium_confidence"
        elif best_candidate['distance'] <= 200:
            final_status = "probable_match"
        else:
            final_status = "invalid_suspected"

        # Update Database
        existing = db.query(OTACoordinateValidation).filter(OTACoordinateValidation.property_raw_id == raw_prop.id).first()
        val_data = {
            "property_raw_id": raw_prop.id,
            "ota_source": raw_prop.ota_source,
            "raw_listing_name": raw_prop.raw_listing_name,
            "raw_listing_id": raw_prop.raw_listing_id,
            "raw_lat": raw_lat,
            "raw_lng": raw_lng,
            "nearest_lodging_name": best_candidate['cand']['canonical_name'],
            "nearest_lodging_distance_m": float(best_candidate['distance']),
            "name_match_status": best_candidate['name_sim'],
            "address_match_status": best_candidate['addr_match'],
            "existence_validation_status": final_status,
            "existence_validation_note": f"Score:{best_candidate['conf_score']}, D:{best_candidate['distance']:.1f}m, N:{best_candidate['name_sim']}",
            "validated_at": datetime.now()
        }
        if existing:
            for key, value in val_data.items(): setattr(existing, key, value)
        else:
            db.add(OTACoordinateValidation(**val_data))
        return val_data

def run_matching():
    db = SessionLocal()
    matcher = EntityMatcher(MASTER_DATA_PATH)
    try:
        targets = db.query(OTAPropertyRaw).filter(OTAPropertyRaw.raw_lat.isnot(None)).all()
        print(f"Processing candidate-aware entity matching for {len(targets)} records...")
        results = []
        for t in targets:
            res = matcher.match_record(db, t)
            if res: results.append(res)
        db.commit()
        
        df = pd.DataFrame(results)
        print("\n### [Entity Matching] 결과 리포트 (Sample)")
        for r in results[:20]:
            print(f"| {r['ota_source']} | {r['raw_listing_name']} | {r['nearest_lodging_name']} | {r['nearest_lodging_distance_m']:.1f} | {r['name_match_status']} | {r['address_match_status']} | {r['existence_validation_status']} |")
        
        print("\n### Matching Status Summary")
        print(df['existence_validation_status'].value_counts())
    finally:
        db.close()

if __name__ == "__main__":
    run_matching()
