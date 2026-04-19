import sys
import os
from sqlalchemy.orm import Session

# Add the root directory to sys.path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal
from app.models.ota_property_raw import OTAPropertyRaw

real_hotels = [
  {
    "name": "L7 홍대 바이 롯데호텔",
    "address": "서울, 마포구 양화로 141",
    "lat": 37.55543874276,
    "lng": 126.92150610352701,
    "url": "https://www.booking.com/hotel/kr/l7-hongdae.ko.html"
  },
  {
    "name": "Hongdae Hue - 1min from Hongik Uni station Exit1",
    "address": "서울, 마포구 양화로 157 10층 1010",
    "lat": 37.5566855,
    "lng": 126.9229417,
    "url": "https://www.booking.com/hotel/kr/hongdae-hue-house.ko.html"
  },
  {
    "name": "홀리데이 인 익스프레스 서울 홍대",
    "address": "서울, 마포구 양화로 188",
    "lat": 37.557498,
    "lng": 126.926772,
    "url": "https://www.booking.com/hotel/kr/holiday-inn-express-seoul-hongdae.ko.html"
  },
  {
    "name": "아만티 호텔 서울 홍대",
    "address": "서울, 31, World Cup buk-ro, Mapo-gu",
    "lat": 37.557061945808,
    "lng": 126.918552517891,
    "url": "https://www.booking.com/hotel/kr/amanti-seoul.ko.html"
  },
  {
    "name": "RYSE, Autograph Collection",
    "address": "서울, 130, Yanghwa-ro, Mapo-gu",
    "lat": 37.554058,
    "lng": 126.921033,
    "url": "https://www.booking.com/hotel/kr/ryse-autograph-collection-korea.ko.html"
  }
]

def inject_real_data():
    db = SessionLocal()
    try:
        for h in real_hotels:
            # Check if exists
            prop = db.query(OTAPropertyRaw).filter_by(raw_listing_url=h["url"]).first()
            if not prop:
                prop = OTAPropertyRaw(
                    ota_source="booking_com",
                    raw_listing_name=h["name"],
                    raw_listing_url=h["url"],
                    raw_address=h["address"],
                    raw_lat=h["lat"],
                    raw_lng=h["lng"],
                    search_area="홍대",
                    search_keyword="Hongdae"
                )
                db.add(prop)
                print(f"Injected: {h['name']}")
            else:
                prop.raw_address = h["address"]
                prop.raw_lat = h["lat"]
                prop.raw_lng = h["lng"]
                print(f"Updated: {h['name']}")
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    inject_real_data()
