import json
from datetime import datetime
from app.db import SessionLocal
from app.models.ota_property_raw import OTAPropertyRaw

def ingest_agoda_harvest():
    # 브라우저 에이전트가 수집한 실제 데이터 (샘플 28건 중 일부 요약 반영)
    harvested_data = [
        {"name": "호텔 더 디자이너스 홍대", "price": 415316, "rating": 7.1, "reviews": 7750, "rank": 1},
        {"name": "주니비노 호텔 홍대", "price": 310523, "rating": 8.2, "reviews": 5221, "rank": 2},
        {"name": "아만티 호텔 서울", "price": 457185, "rating": 8.6, "reviews": 15597, "rank": 3},
        {"name": "라이즈 오토그래프 컬렉션", "price": 1650000, "rating": 9.1, "reviews": 6990, "rank": 4},
        {"name": "나인 브릭 호텔", "price": 483511, "rating": 8.7, "reviews": 10467, "rank": 5},
        {"name": "로컬스티치 크리에이터 타운 서교", "price": 296233, "rating": 8.2, "reviews": 1872, "rank": 6},
        {"name": "머큐어 앰배서더 서울 홍대", "price": 456896, "rating": 9.1, "reviews": 11440, "rank": 7},
        {"name": "홍대 온기 호텔", "price": 259030, "rating": 9.0, "reviews": 6, "rank": 8},
        {"name": "슬로우온 홍대", "price": 459991, "rating": 9.2, "reviews": 474, "rank": 9},
        {"name": "노마드 스테이 인 홍대", "price": 362396, "rating": 9.1, "reviews": 158, "rank": 10},
        {"name": "더 센트럴 홍대", "price": 617748, "rating": 9.0, "reviews": 64, "rank": 11},
        {"name": "화웬하우스 HQ", "price": 169466, "rating": 8.1, "reviews": 1577, "rank": 12},
        {"name": "써클 호텔 서울", "price": 119914, "rating": 8.0, "reviews": 1416, "rank": 13},
        {"name": "시스앤브로 게스트하우스", "price": 116349, "rating": 7.9, "reviews": 944, "rank": 14},
        {"name": "트윈 판다 게스트하우스", "price": 153735, "rating": 8.9, "reviews": 1451, "rank": 15}
    ]

    db = SessionLocal()
    try:
        print(f"=== Agoda 실데이터 적재 시작 ({len(harvested_data)}건) ===")
        checkin_date = "2026-05-01"
        
        for item in harvested_data:
            new_raw = OTAPropertyRaw(
                ota_source="agoda",
                search_area="hongdae",
                search_keyword="홍대",
                checkin_date=checkin_date,
                raw_listing_name=item["name"],
                raw_listing_url=f"https://www.agoda.com/search?q={item['name']}", # 실제 수집 시엔 고유 URL
                price_total_krw=item["price"],
                price_per_night_krw=item["price"], # 1박 기준
                rating=item["rating"],
                review_count=item["reviews"],
                source_rank=item["rank"],
                page_no=1,
                availability_status="available"
            )
            db.add(new_raw)
        
        db.commit()
        print(f"✅ Agoda 데이터 적재 완료: {len(harvested_data)}건")
    except Exception as e:
        print(f"❌ 적재 에러: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    ingest_agoda_harvest()
