import sys
import os
from datetime import datetime, timedelta
import random

# Add root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal
from app.models.ota_property_raw import OTAPropertyRaw
from app.models.ota_room_offer_raw import OTARoomOfferRaw
from app.models.ota_property_entity import OTASnapshot
from app.utils.grader import grade_property

# Real Hongdae Property Seeds
REAL_HOTELS = [
    "L7 Hongdae by Lotte Hotel", "Mercure Ambassador Seoul Hongdae", "RYSE, Autograph Collection",
    "Holiday Inn Express Seoul Hongdae", "Amanti Hotel Seoul Hongdae", "Nine Brick Hotel",
    "Circle Hotel Seoul", "Hotel The Ore", "Glue Hotel", "Heit Hotel", "Nabi Hostel",
    "DW House 2", "Orbit Guesthouse", "Baroato 2nd", "Mono House Hongdae", "Twin Rabbit Guesthouse"
]

REAL_AIRBNB = [
    "Cozy Loft near Hongik Univ Station", "Modern Studio with City View", "Yeonnam-dong Hidden Gem",
    "Traditional Hanok Stay in Se교", "Minimalist Apartment for 4", "Artistic Suite near Club Street"
]

def generate_strategic_hongdae_data():
    db = SessionLocal()
    checkin_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
    
    # 1. Booking.com (Primary) - Real Names
    print("Generating Booking.com (Primary) with Real Names...")
    for i, name in enumerate(REAL_HOTELS * 3): # Duplicate list to get more rows
        if i >= 100: break
        prop = OTAPropertyRaw(
            ota_source="booking_com", source_role="primary",
            raw_listing_name=f"{name} {i // len(REAL_HOTELS)}",
            raw_listing_url=f"https://www.booking.com/h/real_b_{i}.html",
            region_code="hongdae", property_type_std="hotel" if "Hotel" in name else "hostel",
            raw_lat=37.556 + random.uniform(-0.005, 0.005),
            raw_lng=126.923 + random.uniform(-0.005, 0.005),
            geo_precision="exact",
            review_score_std=random.uniform(8.0, 9.5), review_count=random.randint(50, 2000),
            internal_grade=random.choice(["Premium", "Upper-mid", "Standard"])
        )
        db.add(prop); db.flush()
        offer = OTARoomOfferRaw(
            property_raw_id=prop.id, ota_source="booking_com",
            room_type_name="Standard Double", room_analysis_type="double_2p",
            price_per_night_krw=random.randint(120000, 350000), availability_status="available"
        )
        db.add(offer); db.flush()
        db.add(OTASnapshot(property_raw_id=prop.id, room_offer_raw_id=offer.id, ota_source="booking_com", checkin_date=checkin_date, sold_out_yn=False, price_per_night_krw=offer.price_per_night_krw))

    # 2. Airbnb (Area Reference) - Realistic Names
    print("Generating Airbnb (Area Reference) with Real Patterns...")
    for i in range(50):
        name = random.choice(REAL_AIRBNB)
        cluster = random.choice(["Yeonnam", "Seogyo", "Hapjeong"])
        prop = OTAPropertyRaw(
            ota_source="airbnb", source_role="area_reference",
            raw_listing_name=f"{name} in {cluster} #{i}",
            raw_listing_url=f"https://www.airbnb.com/h/real_air_{i}.html",
            region_code="hongdae", area_cluster=cluster,
            geo_precision="approximate_area",
            approx_lat=37.556, approx_lng=126.923,
            review_score_std=random.uniform(4.5, 5.0), review_count=random.randint(10, 200)
        )
        db.add(prop); db.flush()
        db.add(OTARoomOfferRaw(property_raw_id=prop.id, ota_source="airbnb", price_per_night_krw=random.randint(80000, 200000)))

    db.commit()
    print("Strategic Data (Real Names) Seeding Complete.")
    db.close()

if __name__ == "__main__":
    generate_strategic_hongdae_data()
