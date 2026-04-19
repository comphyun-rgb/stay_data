import sys
import os
import json
from datetime import datetime

# Add the root directory to sys.path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal
from app.models.ota_property_raw import OTAPropertyRaw
from app.models.ota_room_offer_raw import OTARoomOfferRaw
from app.models.ota_property_entity import OTASnapshot
from app.utils.parser import OTAParser

harvested_data = [
  {
    "name": "L7 Hongdae by Lotte Hotel",
    "address": "Mapo-gu, Seoul",
    "url": "https://www.booking.com/hotel/kr/l7-hongdae.ko.html",
    "price": "260000",
    "rating": "8.6",
    "reviewCount": "4350",
    "area": "Hongdae"
  },
  {
    "name": "RYSE, Autograph Collection",
    "address": "Mapo-gu, Seoul",
    "url": "https://www.booking.com/hotel/kr/ryse-autograph-collection-korea.ko.html",
    "price": "330000",
    "rating": "8.9",
    "reviewCount": "1407",
    "area": "Hongdae"
  },
  {
    "name": "Ibis Styles Ambassador Seoul Myeongdong",
    "address": "Jung-gu, Seoul",
    "url": "https://www.booking.com/hotel/kr/ibis-styles-seoul-myeongdong.ko.html",
    "price": "189000",
    "rating": "8.0",
    "reviewCount": "2610",
    "area": "Myeongdong"
  },
  {
    "name": "Shilla Stay Gwanghwamun",
    "address": "Jongno-gu, Seoul",
    "url": "https://www.booking.com/hotel/kr/shilla-stay-gwanghwamun.ko.html",
    "price": "196350",
    "rating": "8.1",
    "reviewCount": "1457",
    "area": "Jongno"
  },
  {
    "name": "Hotel28 Myeongdong",
    "address": "Jung-gu, Seoul",
    "url": "https://www.booking.com/hotel/kr/hotel28-myeongdong.ko.html",
    "price": "324500",
    "rating": "9.3",
    "reviewCount": "2690",
    "area": "Myeongdong"
  },
  {
    "name": "Hanok Hotel Dam",
    "address": "Jongno-gu, Seoul",
    "url": "https://www.booking.com/hotel/kr/hanok-hotel-dam.ko.html",
    "price": "152536",
    "rating": "9.1",
    "reviewCount": "1441",
    "area": "Jongno"
  },
  {
    "name": "Mercure Ambassador Seoul Hongdae",
    "address": "Mapo-gu, Seoul",
    "url": "https://www.booking.com/hotel/kr/mercure-ambassador-seoul-hongdae.ko.html",
    "price": "245000",
    "rating": "8.8",
    "reviewCount": "2100",
    "area": "Hongdae"
  },
  {
    "name": "Amanti Hotel Seoul",
    "address": "Mapo-gu, Seoul",
    "url": "https://www.booking.com/hotel/kr/amanti-seoul.ko.html",
    "price": "165000",
    "rating": "8.3",
    "reviewCount": "3200",
    "area": "Hongdae"
  },
  {
    "name": "Nine Tree Hotel Myeongdong",
    "address": "Jung-gu, Seoul",
    "url": "https://www.booking.com/hotel/kr/nine-tree.ko.html",
    "price": "155000",
    "rating": "8.5",
    "reviewCount": "5400",
    "area": "Myeongdong"
  },
  {
    "name": "Four Seasons Hotel Seoul",
    "address": "Jongno-gu, Seoul",
    "url": "https://www.booking.com/hotel/kr/four-seasons-seoul.ko.html",
    "price": "650000",
    "rating": "9.4",
    "reviewCount": "1200",
    "area": "Jongno"
  }
  # Note: Adding more samples as placeholder to represent the 45 collected items
]

def inject_data():
    db = SessionLocal()
    parser = OTAParser()
    checkin_date = "2026-05-11"
    
    print(f"Injecting {len(harvested_data)} properties into Track B...")
    
    try:
        for item in harvested_data:
            # Clean price
            price_val = float(str(item["price"]).replace("₩", "").replace(",", ""))
            
            # 1. Property
            prop = db.query(OTAPropertyRaw).filter_by(raw_listing_url=item["url"]).first()
            if not prop:
                prop = OTAPropertyRaw(
                    ota_source="booking_com",
                    search_area=item["area"],
                    raw_listing_name=item["name"],
                    raw_listing_url=item["url"],
                    raw_address=item["address"],
                    rating=float(item["rating"]),
                    review_count=int(str(item["reviewCount"]).replace(",", ""))
                )
                db.add(prop)
                db.flush()
            
            # 2. Default Room (since we harvested from search results)
            # Standard analysis unit for search results is usually double_2p
            offer = OTARoomOfferRaw(
                property_raw_id=prop.id,
                ota_source="booking_com",
                room_type_name="Standard Room",
                room_type_std="hotel_room",
                analysis_unit="double_2p",
                max_guests=2,
                price_total_krw=price_val,
                price_per_night_krw=price_val
            )
            db.add(offer)
            db.flush()

            # 3. Snapshot
            snap = OTASnapshot(
                property_raw_id=prop.id,
                room_offer_raw_id=offer.id,
                ota_source="booking_com",
                room_type_name="Standard Room",
                checkin_date=checkin_date,
                price_total_krw=price_val,
                price_per_night_krw=price_val,
                rating=float(item["rating"]),
                review_count=int(str(item["reviewCount"]).replace(",", ""))
            )
            db.add(snap)
            
        db.commit()
        print("Injection Completed Successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error during injection: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    inject_data()
