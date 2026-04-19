import sys
import os
import pandas as pd
from sqlalchemy import func, Integer, cast

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.db import SessionLocal
from app.models.ota_property_raw import OTAPropertyRaw
from app.models.ota_room_offer_raw import OTARoomOfferRaw
from app.models.ota_property_entity import OTASnapshot

def reconcile_report():
    db = SessionLocal()
    try:
        print("### [Reconciliation: Report Metric Verification]")
        
        # 1. Property Counts by Grade
        grades = ["Premium", "Upper-mid", "Standard", "Budget"]
        for g in grades:
            cnt = db.query(OTAPropertyRaw).filter(OTAPropertyRaw.internal_grade == g).count()
            print(f"- {g} Property Count: {cnt}")
            
        # 2. Avg Price Re-calculation (Checking if sold-outs are excluded)
        # Using room_offer directly
        price_query = db.query(
            OTAPropertyRaw.internal_grade,
            OTARoomOfferRaw.room_analysis_type,
            func.avg(OTARoomOfferRaw.price_per_night_krw)
        ).join(OTARoomOfferRaw, OTAPropertyRaw.id == OTARoomOfferRaw.property_raw_id)\
         .filter(OTARoomOfferRaw.availability_status == 'available')\
         .group_by(OTAPropertyRaw.internal_grade, OTARoomOfferRaw.room_analysis_type).all()
        
        print("\n#### Re-calculated Avg Prices (Available Only)")
        for g, t, p in price_query:
            print(f"- {g} | {t}: {int(p):,}")

        # 3. Sold-out Rate Re-calculation
        so_query = db.query(
            OTAPropertyRaw.internal_grade,
            func.count(OTASnapshot.id),
            func.sum(cast(OTASnapshot.sold_out_yn, Integer))
        ).join(OTASnapshot, OTAPropertyRaw.id == OTASnapshot.property_raw_id)\
         .group_by(OTAPropertyRaw.internal_grade).all()
         
        print("\n#### Re-calculated Sold-out Rates")
        for g, total, sold in so_query:
            rate = (sold/total*100) if total > 0 else 0
            print(f"- {g}: {sold}/{total} ({rate:.1f}%)")

    finally:
        db.close()

if __name__ == "__main__":
    reconcile_report()
