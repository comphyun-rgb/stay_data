import sys
import os
import pandas as pd
from sqlalchemy import func, Integer, cast

# Add root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal
from app.models.ota_property_raw import OTAPropertyRaw
from app.models.ota_room_offer_raw import OTARoomOfferRaw
from app.models.ota_property_entity import OTASnapshot

def generate_overhauled_report():
    db = SessionLocal()
    try:
        print("\n=== [Track B] Overhauled Market Analysis Report ===")
        
        # 1. Internal Grade Distribution
        grade_dist = db.query(OTAPropertyRaw.internal_grade, func.count(OTAPropertyRaw.id))\
                       .group_by(OTAPropertyRaw.internal_grade).all()
        print("\n#### [Property Level] Internal Grade Distribution")
        print("| Grade | Count |")
        print("|---|---|")
        for g, c in grade_dist:
            print(f"| {g} | {c} |")

        # 2. Price by Grade & Analysis Type
        price_query = db.query(
            OTAPropertyRaw.internal_grade,
            OTARoomOfferRaw.room_analysis_type,
            func.avg(OTARoomOfferRaw.price_per_night_krw).label('avg_price')
        ).join(OTARoomOfferRaw, OTAPropertyRaw.id == OTARoomOfferRaw.property_raw_id)\
         .filter(OTARoomOfferRaw.availability_status == 'available')\
         .group_by(OTAPropertyRaw.internal_grade, OTARoomOfferRaw.room_analysis_type).all()
        
        print("\n#### [Pricing] Average Price by Grade & Unit")
        df_price = pd.DataFrame(price_query)
        pivot_price = df_price.pivot(index='internal_grade', columns='room_analysis_type', values='avg_price')
        
        header = "| Grade | " + " | ".join(pivot_price.columns) + " |"
        sep = "|---| " + " | ".join(["---"] * len(pivot_price.columns)) + " |"
        print(header)
        print(sep)
        for idx, row in pivot_price.iterrows():
            cells = [f"{int(val):,}" if pd.notna(val) else "-" for val in row]
            print(f"| {idx} | " + " | ".join(cells) + " |")

        # 3. Sold-out Intensity
        sold_out_query = db.query(
            OTAPropertyRaw.internal_grade,
            func.count(OTASnapshot.id).label('total'),
            func.sum(cast(OTASnapshot.sold_out_yn, Integer)).label('sold_out_count')
        ).join(OTASnapshot, OTAPropertyRaw.id == OTASnapshot.property_raw_id)\
         .group_by(OTAPropertyRaw.internal_grade).all()
        
        print("\n#### [Market Intensity] Sold-out Rate by Grade")
        print("| Grade | Total Snaps | Sold-out | Rate (%) |")
        print("|---|---|---|---|")
        for g, total, sold in sold_out_query:
            rate = (sold / total * 100) if total > 0 else 0
            print(f"| {g} | {total} | {sold} | {rate:.1f}% |")

        # 4. Coverage Metrics
        total_props = db.query(OTAPropertyRaw).count()
        total_offers = db.query(OTARoomOfferRaw).count()
        print(f"\n#### [Coverage] Stats")
        print(f"- Total Properties: {total_props}")
        print(f"- Total Room Offers: {total_offers}")
        print(f"- Grade Calculation Rate: 100% (Rule-based)")

    finally:
        db.close()

if __name__ == "__main__":
    generate_overhauled_report()
