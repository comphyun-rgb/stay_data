import sys
import os
import argparse
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import DB_PATH
from app.models.ota_property_raw import OTAPropertyRaw
from app.models.ota_room_offer_raw import OTARoomOfferRaw
from app.models.ota_property_entity import OTASnapshot

def get_session():
    engine = create_engine(f"sqlite:///{DB_PATH}")
    Session = sessionmaker(bind=engine)
    return Session()

def show_summary(db):
    print("\n=== [DATA SUMMARY] ===")
    roles = db.query(OTAPropertyRaw.source_role, func.count(OTAPropertyRaw.id)).group_by(OTAPropertyRaw.source_role).all()
    print("\n#### Source Roles:")
    for role, count in roles:
        print(f"- {role}: {count}")
    
    types = db.query(OTAPropertyRaw.property_type_std, func.count(OTAPropertyRaw.id)).group_by(OTAPropertyRaw.property_type_std).all()
    print("\n#### Property Types:")
    for t, count in types:
        print(f"- {t}: {count}")

def list_properties(db, limit=20):
    print(f"\n=== [PROPERTY LIST] (Top {limit}) ===")
    props = db.query(OTAPropertyRaw).limit(limit).all()
    print("| ID | Role | Source | Name | Grade | Region |")
    print("|---|---|---|---|---|---|")
    for p in props:
        print(f"| {p.id} | {p.source_role} | {p.ota_source} | {p.raw_listing_name[:20]} | {p.internal_grade} | {p.region_code} |")

def show_detail(db, prop_id):
    p = db.query(OTAPropertyRaw).filter(OTAPropertyRaw.id == prop_id).first()
    if not p:
        print(f"Property ID {prop_id} not found.")
        return
    
    print(f"\n=== [DETAIL: {p.raw_listing_name}] ===")
    print(f"- Role: {p.source_role} | Source: {p.ota_source}")
    print(f"- Precision: {p.geo_precision} | Cluster: {p.area_cluster}")
    print(f"- Coords: {p.raw_lat}, {p.raw_lng} (Approx: {p.approx_lat}, {p.approx_lng})")
    print(f"- Grade: {p.internal_grade} (Score: {p.total_grade_score})")
    print(f"- Facilities: WiFi({p.wifi_yn}), Elev({p.elevator_yn}), Breakfast({p.breakfast_yn})")
    
    offers = db.query(OTARoomOfferRaw).filter(OTARoomOfferRaw.property_raw_id == prop_id).all()
    print("\n#### Room Offers:")
    for o in offers:
        print(f"  - [{o.id}] {o.room_type_name} ({o.room_analysis_type}): {o.price_per_night_krw:,} KRW | {o.availability_status}")
    
    snaps = db.query(OTASnapshot).filter(OTASnapshot.property_raw_id == prop_id).all()
    print("\n#### Snapshots History:")
    for s in snaps:
        print(f"  - {s.search_date} (Checkin: {s.checkin_date}): {s.price_per_night_krw:,} KRW | SoldOut: {s.sold_out_yn}")

if __name__ == "__main__":
    from sqlalchemy import func
    parser = argparse.ArgumentParser(description="Track B Data Explorer")
    parser.add_argument("--summary", action="store_true", help="Show data summary")
    parser.add_argument("--list", action="store_true", help="List properties")
    parser.add_argument("--id", type=int, help="Show detail for property ID")
    
    args = parser.parse_args()
    db = get_session()
    
    if args.summary:
        show_summary(db)
    elif args.list:
        list_properties(db)
    elif args.id:
        show_detail(db, args.id)
    else:
        show_summary(db)
        list_properties(db, limit=5)
        print("\nUse --id [ID] to see full details.")
    
    db.close()
