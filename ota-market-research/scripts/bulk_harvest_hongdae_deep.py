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
from app.utils.parser import OTAParser
from app.utils.grader import grade_property

# Hongdae Central Point
HONGDAE_STN_LAT = 37.556
HONGDAE_STN_LNG = 126.923

REAL_SEEDS = [
    {"name": "L7 Hongdae by Lotte Hotel", "price": 260000, "rating": 8.6, "reviews": 4350, "star": 4.0, "lat": 37.555, "lng": 126.922, "type": "hotel"},
    {"name": "Mercure Ambassador Seoul Hongdae", "price": 249280, "rating": 9.0, "reviews": 2100, "star": 4.0, "lat": 37.557, "lng": 126.924, "type": "hotel"},
    {"name": "RYSE, Autograph Collection", "price": 330000, "rating": 8.9, "reviews": 1407, "star": 4.5, "lat": 37.554, "lng": 126.921, "type": "hotel"},
    {"name": "Holiday Inn Express Seoul Hongdae", "price": 260425, "rating": 8.7, "reviews": 3500, "star": 3.5, "lat": 37.558, "lng": 126.925, "type": "hotel"},
    {"name": "Nabi Hostel", "price": 118912, "rating": 8.5, "reviews": 1100, "star": 0.0, "lat": 37.553, "lng": 126.920, "type": "hostel"}
]

def generate_refined_hongdae_data(count=150):
    db = SessionLocal()
    parser = OTAParser()
    checkin_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
    
    print(f"Generating {count} Refined properties (Real Coords & Facility Parsing)...")
    
    try:
        for i in range(count):
            if i < len(REAL_SEEDS):
                s = REAL_SEEDS[i]
                name, price, rating, reviews = s["name"], s["price"], s["rating"], s["reviews"]
                star, lat, lng, p_type = s["star"], s["lat"], s["lng"], s["type"]
            else:
                p_type = random.choice(["hotel", "hostel", "guesthouse", "apartment"])
                name = f"Hongdae {p_type.capitalize()} {i+100}"
                price = random.randint(40000, 250000)
                rating = round(random.uniform(7.0, 9.5), 1)
                reviews = random.randint(5, 500)
                star = random.choice([0.0, 2.0, 3.0]) if p_type == "hotel" else 0.0
                # Random coords within 1.5km
                lat = HONGDAE_STN_LAT + random.uniform(-0.01, 0.01)
                lng = HONGDAE_STN_LNG + random.uniform(-0.01, 0.01)

            # 1. Facility Parsing Mocking
            facility_text = "Free WiFi, Air conditioning, " + random.choice(["Elevator, Breakfast", "Shared Kitchen", "Private Bathroom"])
            fac_parsed = parser.parse_facilities(facility_text)
            
            # 2. Create Property
            prop = OTAPropertyRaw(
                ota_source="booking_com",
                raw_listing_name=name,
                raw_listing_url=f"https://www.booking.com/h/hd_ref_{i}.html",
                region_code="hongdae",
                property_type_std=p_type,
                official_star_rating=star,
                raw_lat=lat,
                raw_lng=lng,
                review_score_std=rating,
                review_count=reviews,
                facility_text_raw=facility_text,
                **fac_parsed
            )
            
            # 3. Apply Internal Grading (Real Coords)
            grading = grade_property({
                "raw_lat": lat,
                "raw_lng": lng,
                "review_score_std": rating,
                "review_count": reviews,
                "property_type_std": p_type,
                "official_star_rating": star,
                **fac_parsed
            })
            for k, v in grading.items():
                if k == 'note': prop.grade_reason_note = v
                else: setattr(prop, k, v)
                
            db.add(prop)
            db.flush()
            
            # 4. Rooms
            room_configs = [("Standard Double", "hotel_room", "double_2p", 2, 1.0)]
            for r_name, r_std, a_type, guests, mult in room_configs:
                offer = OTARoomOfferRaw(
                    property_raw_id=prop.id, ota_source="booking_com",
                    room_type_name=r_name, room_type_std=r_std,
                    room_analysis_type=a_type, max_guests=guests,
                    price_total_krw=price * mult, price_per_night_krw=price * mult,
                    availability_status="available"
                )
                db.add(offer)
                db.flush()
                db.add(OTASnapshot(
                    property_raw_id=prop.id, room_offer_raw_id=offer.id,
                    ota_source="booking_com", checkin_date=checkin_date,
                    scrape_success_yn=True, observed_price_yn=True,
                    sold_out_yn=False, bookable_yn=True,
                    price_total_krw=price * mult, price_per_night_krw=price * mult
                ))
                
        db.commit()
        print(f"Refinement Complete: {count} properties injected with real coordinate scoring.")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    generate_refined_hongdae_data(150)
