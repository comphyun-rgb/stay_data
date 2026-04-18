import random
from app.collectors.agoda import AgodaCollector
from app.collectors.booking import BookingCollector

def generate_bulk_data(count=100):
    ota_list = []
    keywords = ["홍대", "연남동", "합정", "상수", "서교동", "신촌"]
    property_types = ["Hotel", "Guesthouse", "Hostel", "Apartment"]
    
    for i in range(1, count + 1):
        # 숙소 기본 정보
        p_type = random.choice(property_types)
        name = f"Hongdae {p_type} {i}"
        url = f"https://www.ota.com/h/{i}"
        lat = 37.55 + (random.random() * 0.02)
        lng = 126.91 + (random.random() * 0.02)
        star = random.choice([2.0, 3.0, 4.0, 5.0]) if p_type == "Hotel" else None
        
        # 객실 정보 (1~3개)
        rooms = []
        for j in range(random.randint(1, 3)):
            r_name = random.choice(["Standard", "Deluxe", "Superior", "Dorm Bed"])
            price = random.randint(30000, 500000)
            rooms.append({
                "name": f"{r_name} Room {j}",
                "price": price,
                "guests": f"{random.randint(1,4)}인",
                "bathroom": random.choice(["Private Bathroom", "Shared Bathroom"]),
                "policy": random.choice(["Free Cancellation", "Non-refundable"]),
                "tax": "Tax Included"
            })
            
        ota_list.append({
            "id": f"OTA_{i}",
            "name": name,
            "url": url,
            "lat": lat,
            "lng": lng,
            "property_type": p_type,
            "star_rating": star,
            "rooms": rooms,
            "keyword": random.choice(keywords)
        })
    return ota_list

def run_bulk_harvest():
    print("=== [Phase 6] 홍대권 100+ 숙소 전수 수집 시작 ===")
    
    # 1. 120개 샘플 데이터 생성 (중복 테스트를 위해 120개)
    bulk_data = generate_bulk_data(120)
    
    agoda = AgodaCollector()
    booking = BookingCollector()
    
    # 2. 키워드별로 나눠서 적재 (Deduplication 테스트)
    keywords = ["홍대", "연남동", "합정", "상수", "서교동", "신촌"]
    
    for kw in keywords:
        kw_items = [item for item in bulk_data if item["keyword"] == kw]
        # 일부 데이터는 여러 키워드에 중복 노출됨을 가정
        extra_items = random.sample(bulk_data, 5) # 5개는 무조건 중복 노출
        
        print(f"\n--- 키워드 '{kw}' 적재 ({len(kw_items)} + 중복 {len(extra_items)}건) ---")
        
        # Agoda 적재
        agoda._save_to_db(kw_items + extra_items, "hongdae", kw, "2026-05-01", 1)
        
        # Booking 적재 (동일 데이터의 타 채널 노출 가정)
        booking._save_to_db(kw_items[:5], "hongdae", kw, "2026-05-01", 1)

    print("\nDONE: Bulk Harvesting 완료!")

if __name__ == "__main__":
    run_bulk_harvest()
