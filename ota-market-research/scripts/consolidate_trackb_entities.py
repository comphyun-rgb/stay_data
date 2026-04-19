import sys
import os
import pandas as pd
from sqlalchemy.orm import Session
from datetime import datetime

# Add root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal
from app.models.ota_property_raw import OTAPropertyRaw
from app.models.ota_property_entity import OTAPropertyEntity
from app.utils.matcher import calculate_name_similarity, get_similarity_level
from app.utils.grader import calculate_haversine_distance

def consolidate_entities():
    db = SessionLocal()
    try:
        # 1. Clear existing entities for a fresh run
        db.query(OTAPropertyEntity).delete()
        db.execute(text("UPDATE ota_property_raw SET entity_id = NULL"))
        db.commit()

        # 2. Get all primary properties (Booking.com)
        primaries = db.query(OTAPropertyRaw).filter(OTAPropertyRaw.source_role == 'primary').all()
        print(f"Consolidating {len(primaries)} Primary (Booking.com) entities...")

        for p in primaries:
            # Create a new Consolidated Entity
            entity = OTAPropertyEntity(
                canonical_name=p.raw_listing_name,
                representative_address=p.raw_address,
                lat=p.raw_lat,
                lng=p.raw_lng,
                note=f"Created from Primary ID: {p.id}"
            )
            db.add(entity)
            db.flush()
            
            # Link back to the raw record
            p.entity_id = entity.id
            
            # 3. Match Secondary (Agoda) & Area Reference (Airbnb)
            others = db.query(OTAPropertyRaw).filter(
                OTAPropertyRaw.source_role != 'primary',
                OTAPropertyRaw.entity_id.is_(None)
            ).all()
            
            for other in others:
                # Name Similarity
                name_score = calculate_name_similarity(p.raw_listing_name, other.raw_listing_name)
                name_level = get_similarity_level(name_score)
                
                # Distance Check
                dist = 9999
                if p.raw_lat and other.raw_lat:
                    dist = calculate_haversine_distance(p.raw_lat, p.raw_lng, other.raw_lat, other.raw_lng)
                elif p.raw_lat and other.approx_lat:
                    dist = calculate_haversine_distance(p.raw_lat, p.raw_lng, other.approx_lat, other.approx_lng)

                # Match Criteria: (High Name Match OR (Med Name Match AND Close Distance))
                if name_level == 'exact' or (name_level == 'high' and dist < 100) or (dist < 50):
                    other.entity_id = entity.id
                    # print(f"  [Match] {other.ota_source}:{other.raw_listing_name} -> {entity.canonical_name}")

        db.commit()
        
        # 4. Handle remaining others (those without a primary match)
        remains = db.query(OTAPropertyRaw).filter(OTAPropertyRaw.entity_id.is_(None)).all()
        print(f"Processing {len(remains)} orphaned properties as independent entities...")
        for r in remains:
            entity = OTAPropertyEntity(
                canonical_name=r.raw_listing_name,
                lat=r.raw_lat or r.approx_lat,
                lng=r.raw_lng or r.approx_lng,
                note=f"Independent Entity from {r.ota_source} ID: {r.id}"
            )
            db.add(entity); db.flush()
            r.entity_id = entity.id
            
        db.commit()
        
        # Summary
        entity_count = db.query(OTAPropertyEntity).count()
        raw_count = db.query(OTAPropertyRaw).count()
        print(f"\nConsolidation Complete.")
        print(f"- Total Raw Listings: {raw_count}")
        print(f"- Total Consolidated Entities: {entity_count}")
        print(f"- Average Listings per Entity: {raw_count/entity_count:.2f}")

    finally:
        db.close()

if __name__ == "__main__":
    from sqlalchemy import text
    consolidate_entities()
