import sys
import os
import pandas as pd
from sqlalchemy import func

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.db import SessionLocal
from app.models.ota_room_offer_raw import OTARoomOfferRaw

def audit_roomtype():
    db = SessionLocal()
    try:
        # A. Distributions
        type_std = db.query(OTARoomOfferRaw.room_type_std, func.count(OTARoomOfferRaw.id)).group_by(OTARoomOfferRaw.room_type_std).all()
        analysis_type = db.query(OTARoomOfferRaw.room_analysis_type, func.count(OTARoomOfferRaw.id)).group_by(OTARoomOfferRaw.room_analysis_type).all()
        guests_dist = db.query(OTARoomOfferRaw.max_guests, func.count(OTARoomOfferRaw.id)).group_by(OTARoomOfferRaw.max_guests).all()

        print(f"### [Audit: Room Type Distributions]")
        print("\n#### Standard Types")
        for t, c in type_std: print(f"- {t}: {c}")
        
        print("\n#### Analysis Types")
        for t, c in analysis_type: print(f"- {t}: {c}")
        
        print("\n#### Max Guests")
        for g, c in guests_dist: print(f"- {g} guests: {c}")

        # B. Classification Audit
        # 1. Other but might be classifiable
        other_list = db.query(OTARoomOfferRaw).filter(OTARoomOfferRaw.room_analysis_type == 'other').limit(10).all()
        # 2. Double but guests >= 3
        mismatch1 = db.query(OTARoomOfferRaw).filter(OTARoomOfferRaw.room_analysis_type == 'double_2p', OTARoomOfferRaw.max_guests >= 3).count()
        # 3. Family but guests <= 2
        mismatch2 = db.query(OTARoomOfferRaw).filter(OTARoomOfferRaw.room_analysis_type == 'family_4p', OTARoomOfferRaw.max_guests <= 2).count()
        
        print(f"\n### [Audit: Classification Anomalies]")
        print(f"- double_2p with guests >= 3: {mismatch1}")
        print(f"- family_4p with guests <= 2: {mismatch2}")

        # C. Sample Table (30 rows)
        samples = db.query(OTARoomOfferRaw).limit(30).all()
        print("\n### [Audit: Room Mapping Samples]")
        cols = ["room_type_name", "room_type_std", "room_analysis_type", "max_guests", "private_bathroom_yn"]
        print("| " + " | ".join(cols) + " |")
        print("|" + "|".join(["---"] * len(cols)) + "|")
        for s in samples:
            vals = [str(getattr(s, c)) for c in cols]
            print("| " + " | ".join(vals) + " |")

    finally:
        db.close()

if __name__ == "__main__":
    audit_roomtype()
