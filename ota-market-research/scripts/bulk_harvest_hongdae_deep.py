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

# Real Seeds (Extended for Overhaul)
REAL_SEEDS = [
    {"name": "L7 Hongdae by Lotte Hotel", "price": 260000, "rating": 8.6, "reviews": 4350, "star": 4.0, "dist": 50, "type": "hotel"},
    {"name": "Mercure Ambassador Seoul Hongdae", "price": 249280, "rating": 9.0, "reviews": 2100, "star": 4.0, "dist": 150, "type": "hotel"},
    {"name": "RYSE, Autograph Collection", "price": 330000, "rating": 8.9, "reviews": 1407, "star": 4.5, "dist": 250, "type": "hotel"},
    {"name": "Holiday Inn Express Seoul Hongdae", "price": 260425, "rating": 8.7, "reviews": 3500, "star": 3.5, "dist": 100, "type": "hotel"},
    {"name": "Amanti Hotel Seoul Hongdae", "price": 242000, "rating": 8.7, "reviews": 3200, "star": 4.0, "dist": 450, "type": "hotel"},
    {"name": "Nabi Hostel", "price": 118912, "rating": 8.5, "reviews": 1100, "star": 0.0, "dist": 200, "type": "hostel"},
    {"name": "DW House 2", "price": 135000, "rating": 8.4, "reviews": 210, "star": 0.0, "dist": 600, "type": "guesthouse"},
    {"name": "i18 Hongdae city view", "price": 130272, "rating": 9.6, "reviews": 85, "star": 0.0, "dist": 300, "type": "apartment"}
]

def generate_overhauled_hongdae_data(count=150):
    db = SessionLocal()
    parser = OTAParser()
    checkin_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
    collected_at = datetime.now()
    
    print(f"Generating {count} properties with Overhauled Model (Grades & Analysis Types)...")
    
    try:
        for i in range(count):
            if i < len(REAL_SEEDS):
                s = REAL_SEEDS[i]
                name, price, rating, reviews = s["name"], s["price"], s["rating"], s["reviews"]
                star, dist, p_type = s["star"], s["dist"], s["type"]
            else:
                p_type = random.choice(["hotel", "hostel", "guesthouse", "apartment"])
                name = f"Hongdae {p_type.capitalize()} {i+100}"
                price = random.randint(40000, 250000)
                rating = round(random.uniform(7.0, 9.5), 1)
                reviews = random.randint(5, 500)
                star = random.choice([0.0, 2.0, 3.0]) if p_type == "hotel" else 0.0
                dist = random.randint(50, 2000)

            # 1. Create Property
            prop = OTAPropertyRaw(
                ota_source="booking_com",
                raw_listing_name=name,
                raw_listing_url=f"https://www.booking.com/h/hd_{i}.html",
                region_code="hongdae",
                region_label="홍대권",
                property_type_std=p_type,
                official_star_rating=star,
                station_distance_m=dist,
                review_score_std=rating,
                review_count=reviews,
                # Facilities (Random for mock)
                private_bathroom_yn='Y' if p_type != 'hostel' or random.random() > 0.5 else 'N',
                elevator_yn='Y' if p_type == 'hotel' else random.choice(['Y', 'N']),
                breakfast_yn=random.choice(['Y', 'N']),
                wifi_yn='Y',
                aircon_yn='Y'
            )
            
            # 2. Apply Internal Grading
            grading = grade_property({
                "station_distance_m": dist,
                "review_score_std": rating,
                "review_count": reviews,
                "private_bathroom_yn": prop.private_bathroom_yn,
                "elevator_yn": prop.elevator_yn,
                "breakfast_yn": prop.breakfast_yn,
                "wifi_yn": prop.wifi_yn,
                "aircon_yn": prop.aircon_yn,
                "property_type_std": p_type,
                "official_star_rating": star
            })
            for k, v in grading.items():
                if k == 'note': prop.grade_reason_note = v
                else: setattr(prop, k, v)
                
            db.add(prop)
            db.flush()
            
            # 3. Create Room Offers
            room_configs = [
                ("Standard Double", "hotel_room", "double_2p", 2, 1.0),
                ("Dormitory Bed", "dorm_bed", "dorm_1p", 1, 0.3),
                ("Family Suite", "family_room", "family_4p", 4, 2.5)
            ]
            
            for r_name, r_std, a_type, guests, mult in room_configs:
                if a_type == "dorm_1p" and p_type == "hotel": continue
                if a_type == "family_4p" and price < 100000: continue
                
                final_price = price * mult
                is_sold_out = random.random() < 0.15 # 15% sold out rate
                
                offer = OTARoomOfferRaw(
                    property_raw_id=prop.id,
                    ota_source="booking_com",
                    room_type_name=r_name,
                    room_type_std=r_std,
                    room_analysis_type=a_type,
                    max_guests=guests,
                    price_total_krw=final_price if not is_sold_out else 0,
                    price_per_night_krw=final_price if not is_sold_out else 0,
                    availability_status="sold_out" if is_sold_out else "available"
                )
                db.add(offer)
                db.flush()

                # 4. Snapshot
                snap = OTASnapshot(
                    property_raw_id=prop.id,
                    room_offer_raw_id=offer.id,
                    ota_source="booking_com",
                    search_date=collected_at.strftime("%Y-%m-%d"),
                    checkin_date=checkin_date,
                    scrape_success_yn=True,
                    observed_price_yn=not is_sold_out,
                    sold_out_yn=is_sold_out,
                    bookable_yn=not is_sold_out,
                    price_total_krw=final_price if not is_sold_out else 0,
                    price_per_night_krw=final_price if not is_sold_out else 0,
                    availability_text_raw="Sold out" if is_sold_out else "Available"
                )
                db.add(snap)
                
        db.commit()
        print(f"Overhauled Data Injection Complete: {count} properties.")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    generate_overhauled_hongdae_data(150)
