import sys
import os
import pandas as pd
import numpy as np

# Add the root directory to sys.path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal
from app.models.ota_property_raw import OTAPropertyRaw
from app.utils.matcher import normalize_name, calculate_name_similarity, get_similarity_level, normalize_address

MASTER_DATA_PATH = r"c:\stay_data\stay_data\seoul-stay-market-research\data\exports\property_master_full.csv"

def calculate_distance_vectorized(lat1, lon1, lat2, lon2):
    R = 6371000
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c

def debug_matching():
    master_df = pd.read_csv(MASTER_DATA_PATH).dropna(subset=['lat', 'lng'])
    db = SessionLocal()
    
    # Get only the real hotels I injected
    targets = db.query(OTAPropertyRaw).filter(OTAPropertyRaw.raw_listing_url.like('%booking.com/hotel/kr/%')).all()
    
    print(f"Debugging {len(targets)} real properties...")
    
    for t in targets:
        distances = calculate_distance_vectorized(t.raw_lat, t.raw_lng, master_df['lat'].values, master_df['lng'].values)
        top_indices = np.argsort(distances)[:50]
        candidates = master_df.iloc[top_indices].copy()
        candidates['distance'] = distances[top_indices]
        
        print(f"\n[Property: {t.raw_listing_name}]")
        print(f"Address: {t.raw_address}")
        
        best_cand = None
        max_score = -1
        
        for _, cand in candidates.iterrows():
            name_score = calculate_name_similarity(t.raw_listing_name, cand['canonical_name'])
            name_sim = get_similarity_level(name_score)
            
            addr_data_t = normalize_address(t.raw_address)
            addr_data_c = normalize_address(cand['address_road'])
            
            addr_match = "mismatch"
            if addr_data_t['street'] and addr_data_c['street']:
                if addr_data_t['street'] == addr_data_c['street']:
                    addr_match = "exact_match"
            
            score = 0
            if cand['distance'] <= 150: score += 20
            elif cand['distance'] <= 300: score += 10
            
            if name_sim == "exact": score += 60
            elif name_sim == "high": score += 40
            
            if addr_match == "exact_match": score += 100
            
            if "L7" in cand['canonical_name'] or "Holiday" in cand['canonical_name'] or "Amanti" in cand['canonical_name']:
                print(f"  - Cand: {cand['canonical_name']} | Dist: {cand['distance']:.1f} | NameSim: {name_sim} | AddrMatch: {addr_match} | Score: {score}")

            if score > max_score:
                max_score = score
                best_cand = cand

        print(f"  >> Best: {best_cand['canonical_name']} | Max Score: {max_score}")

    db.close()

if __name__ == "__main__":
    debug_matching()
