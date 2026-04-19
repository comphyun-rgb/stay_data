import sys
import os
import pandas as pd
from sqlalchemy import func, Integer, cast

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.db import SessionLocal
from app.models.ota_property_raw import OTAPropertyRaw
from app.models.ota_room_offer_raw import OTARoomOfferRaw
from app.models.ota_property_entity import OTASnapshot

def audit_soldout():
    db = SessionLocal()
    try:
        # A. Status Field Filling Rate
        total = db.query(OTASnapshot).count()
        sold_out_y = db.query(OTASnapshot).filter(OTASnapshot.sold_out_yn == True).count()
        sold_out_n = db.query(OTASnapshot).filter(OTASnapshot.sold_out_yn == False).count()
        
        bookable_y = db.query(OTASnapshot).filter(OTASnapshot.bookable_yn == True).count()
        obs_price_y = db.query(OTASnapshot).filter(OTASnapshot.observed_price_yn == True).count()
        scrape_success_y = db.query(OTASnapshot).filter(OTASnapshot.scrape_success_yn == True).count()
        
        has_avail_text = db.query(OTASnapshot).filter(OTASnapshot.availability_text_raw.isnot(None)).count()
        has_hint_text = db.query(OTASnapshot).filter(OTASnapshot.inventory_hint_text_raw.isnot(None)).count()

        print(f"### [Audit: Availability Fields]")
        print(f"- Total Snapshots: {total}")
        print(f"- sold_out_yn=Y: {sold_out_y} | N: {sold_out_n}")
        print(f"- bookable_yn=Y: {bookable_y}")
        print(f"- observed_price_yn=Y: {obs_price_y}")
        print(f"- scrape_success_yn=Y: {scrape_success_y}")
        print(f"- availability_text_raw exists: {has_avail_text}")
        print(f"- inventory_hint_text_raw exists: {has_hint_text}")

        # B. Consistency Checks
        combo1 = db.query(OTASnapshot).filter(OTASnapshot.sold_out_yn == True, OTASnapshot.observed_price_yn == False).count()
        combo2 = db.query(OTASnapshot).filter(OTASnapshot.sold_out_yn == True, OTASnapshot.scrape_success_yn == False).count()
        combo3 = db.query(OTASnapshot).filter(OTASnapshot.sold_out_yn == False, OTASnapshot.observed_price_yn == False).count()
        combo4 = db.query(OTASnapshot).filter(OTASnapshot.bookable_yn == True, OTASnapshot.sold_out_yn == True).count()
        combo5 = db.query(OTASnapshot).filter(OTASnapshot.observed_price_yn == True, OTASnapshot.price_total_krw.is_(None)).count()
        combo6 = db.query(OTASnapshot).filter(OTASnapshot.observed_price_yn == True, OTASnapshot.price_total_krw == 0).count()

        print(f"\n### [Audit: Consistency Combinations]")
        print(f"- SoldOut=Y & ObsPrice=N (Expected): {combo1}")
        print(f"- SoldOut=Y & ScrapeSuccess=N (Possible Error): {combo2}")
        print(f"- SoldOut=N & ObsPrice=N (Anomaly): {combo3}")
        print(f"- Bookable=Y & SoldOut=Y (Conflict): {combo4}")
        print(f"- ObsPrice=Y & Price is NULL: {combo5}")
        print(f"- ObsPrice=Y & Price is 0: {combo6}")

        # C. Sample (20 rows)
        samples = db.query(OTASnapshot).join(OTAPropertyRaw).limit(20).all()
        print("\n### [Audit: Sold-out Samples]")
        cols = ["property_raw_id", "ota_source", "checkin_date", "price_total_krw", "sold_out_yn", "bookable_yn", "observed_price_yn", "scrape_success_yn", "availability_text_raw"]
        print("| " + " | ".join(cols) + " |")
        print("|" + "|".join(["---"] * len(cols)) + "|")
        for s in samples:
            vals = [str(getattr(s, c)) for c in cols]
            print("| " + " | ".join(vals) + " |")

    finally:
        db.close()

if __name__ == "__main__":
    audit_soldout()
