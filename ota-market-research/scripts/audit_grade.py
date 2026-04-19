import sys
import os
import pandas as pd
from sqlalchemy import func

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.db import SessionLocal
from app.models.ota_property_raw import OTAPropertyRaw
from app.models.ota_room_offer_raw import OTARoomOfferRaw
from app.models.ota_property_entity import OTASnapshot

def audit_grade():
    db = SessionLocal()
    try:
        # A. Baseline Stats
        total_props = db.query(OTAPropertyRaw).filter(OTAPropertyRaw.region_code == 'hongdae').count()
        total_offers = db.query(OTARoomOfferRaw).join(OTAPropertyRaw).filter(OTAPropertyRaw.region_code == 'hongdae').count()
        total_snaps = db.query(OTASnapshot).join(OTAPropertyRaw).filter(OTAPropertyRaw.region_code == 'hongdae').count()
        
        print(f"### [Audit: Baseline] Hongdae Region")
        print(f"- Total Properties: {total_props}")
        print(f"- Total Room Offers: {total_offers}")
        print(f"- Total Snapshots: {total_snaps}")

        # B. Grade Data Filling Rate
        has_internal = db.query(OTAPropertyRaw).filter(OTAPropertyRaw.internal_grade.isnot(None)).count()
        is_null_internal = db.query(OTAPropertyRaw).filter(OTAPropertyRaw.internal_grade.is_(None)).count()
        has_score = db.query(OTAPropertyRaw).filter(OTAPropertyRaw.total_grade_score > 0).count()
        has_star = db.query(OTAPropertyRaw).filter(OTAPropertyRaw.official_star_rating > 0).count()
        has_std_type = db.query(OTAPropertyRaw).filter(OTAPropertyRaw.property_type_std.isnot(None)).count()

        print(f"\n### [Audit: Data Filling]")
        print(f"- Internal Grade exists: {has_internal}")
        print(f"- Internal Grade is NULL: {is_null_internal}")
        print(f"- Score > 0: {has_score}")
        print(f"- Official Star > 0: {has_star}")
        print(f"- Property Type Std exists: {has_std_type}")

        # C. Grade Distribution & Averages
        dist_query = db.query(
            OTAPropertyRaw.internal_grade,
            func.count(OTAPropertyRaw.id).label('count'),
            func.avg(OTAPropertyRaw.total_grade_score).label('avg_score'),
            func.avg(OTAPropertyRaw.review_score_std).label('avg_rev'),
            func.avg(OTAPropertyRaw.review_count).label('avg_rev_count'),
            func.avg(OTAPropertyRaw.official_star_rating).label('avg_star')
        ).group_by(OTAPropertyRaw.internal_grade).all()
        
        print("\n### [Audit: Grade Distribution]")
        print("| Grade | Count | Avg Score | Avg Review | Avg Rev Count | Avg Star |")
        print("|---|---|---|---|---|---|")
        for g, c, s, r, rc, st in dist_query:
            print(f"| {g or 'NULL'} | {c} | {s:.1f} | {r:.1f} | {int(rc)} | {st:.1f} |")

        # D. Sample Table (20 rows)
        samples = db.query(OTAPropertyRaw).limit(20).all()
        print("\n### [Audit: Sample Table (Top 20)]")
        cols = ["raw_listing_name", "ota_source", "property_type_std", "official_star_rating", "location_score", "facility_score", "review_score_component", "scale_score", "total_grade_score", "internal_grade"]
        print("| " + " | ".join(cols) + " |")
        print("|" + "|".join(["---"] * len(cols)) + "|")
        for s in samples:
            vals = [str(getattr(s, c)) for c in cols]
            print("| " + " | ".join(vals) + " |")

    finally:
        db.close()

if __name__ == "__main__":
    audit_grade()
