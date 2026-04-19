import sys
import os
import pandas as pd
import numpy as np
from sqlalchemy import func, Integer, cast

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.db import SessionLocal
from app.models.ota_property_raw import OTAPropertyRaw
from app.models.ota_room_offer_raw import OTARoomOfferRaw
from app.models.ota_property_entity import OTASnapshot
from app.utils.grader import calculate_haversine_distance

HONGDAE_STN_LAT = 37.556
HONGDAE_STN_LNG = 126.923

def run_full_audit():
    db = SessionLocal()
    try:
        # Load data into DataFrames for easier analysis
        props = pd.read_sql(db.query(OTAPropertyRaw).statement, db.bind)
        offers = pd.read_sql(db.query(OTARoomOfferRaw).statement, db.bind)
        snaps = pd.read_sql(db.query(OTASnapshot).statement, db.bind)
        
        # Filter for Hongdae
        hong_props = props[props['region_code'] == 'hongdae']
        hong_offers = offers[offers['property_raw_id'].isin(hong_props['id'])]
        hong_snaps = snaps[snaps['property_raw_id'].isin(hong_props['id'])]

        print("--- AUDIT START ---")
        
        # 1. Coverage Stats
        print("\n[COVERAGE]")
        print(f"Total Props: {len(hong_props)}")
        print(f"Total Offers: {len(hong_offers)}")
        print(f"Total Snaps: {len(hong_snaps)}")
        print("\nOTA Source Dist:")
        print(hong_props['ota_source'].value_counts())
        print("\nProperty Type Std Dist:")
        print(hong_props['property_type_std'].value_counts())
        print("\nInternal Grade Dist:")
        print(hong_props['internal_grade'].value_counts())
        print("\nData Filling Rates:")
        print(f"Lat/Lng Rate: {hong_props['raw_lat'].notnull().mean()*100:.1f}%")
        print(f"Facility Text Rate: {hong_props['facility_text_raw'].notnull().mean()*100:.1f}%")
        print(f"Rating Rate: {hong_props['review_score_std'].notnull().mean()*100:.1f}%")

        # 2. Usability / Price Sanity
        print("\n[PRICING & USABILITY]")
        avail_offers = hong_offers[hong_offers['availability_status'] == 'available']
        price_stats = avail_offers.groupby('room_analysis_type')['price_per_night_krw'].agg(['count', 'mean', 'median', 'min', 'max'])
        print(price_stats)
        
        # 3. Grade Distribution Analysis
        print("\n[GRADE ANALYSIS]")
        grade_stats = hong_props.groupby('internal_grade')['total_grade_score'].agg(['count', 'min', 'median', 'max', 'mean'])
        print(grade_stats)

        # 4. Facility Parsing Audit
        print("\n[FACILITY PARSING]")
        fac_cols = ['wifi_yn', 'breakfast_yn', 'elevator_yn', 'parking_yn', 'kitchen_yn', 'laundry_yn', 'aircon_yn']
        for col in fac_cols:
            print(f"{col}: {hong_props[col].value_counts().get('Y', 0)} / {len(hong_props)}")
            
        # 5. Location Scoring Audit
        print("\n[LOCATION SCORING]")
        if not hong_props.empty:
            dists = hong_props.apply(lambda row: calculate_haversine_distance(row['raw_lat'], row['raw_lng'], HONGDAE_STN_LAT, HONGDAE_STN_LNG), axis=1)
            print(f"Distance stats (m): {dists.describe()}")
            print("\nDistance buckets:")
            print(pd.cut(dists, bins=[0, 300, 700, 1200, 2000, 10000]).value_counts())

        # 6. Snapshot Time Series
        print("\n[SNAPSHOT TIME SERIES]")
        snap_counts = hong_snaps.groupby('room_offer_raw_id').size()
        print(f"Snapshots per offer: {snap_counts.describe()}")
        print(f"Offers with >1 snap: {(snap_counts > 1).sum()}")

        # 7. Duplicates
        print("\n[DUPLICATES]")
        url_dupes = hong_props['raw_listing_url'].duplicated().sum()
        print(f"URL Duplicates: {url_dupes}")

        print("\n--- AUDIT END ---")

    finally:
        db.close()

if __name__ == "__main__":
    run_full_audit()
