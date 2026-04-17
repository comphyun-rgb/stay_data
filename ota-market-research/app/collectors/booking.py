from datetime import datetime, timedelta
from app.models.ota_property_raw import OTAPropertyRaw
from app.db import SessionLocal

class BookingCollector:
    """
    Booking.com 지역 검색 결과 기반 리스팅 수집기.
    """
    def __init__(self):
        self.source_name = "booking_com"

    def collect_by_area(self, area_name: str, checkin_offset: int = 14, nights: int = 1):
        checkin_date = (datetime.now() + timedelta(days=checkin_offset)).strftime("%Y-%m-%d")
        print(f"[{self.source_name}] '{area_name}' 지역 샘플 수집 시작")
        
        # [실제 수집 시엔 Booking.com 검색 결과 파싱 로직 포함]
        results = [
            {"name": "L7 홍대 바이 롯데", "price": 385000, "rating": 8.7, "reviews": 3200},
            {"name": "홀리데이 인 익스프레스 서울 홍대", "price": 312000, "rating": 8.5, "reviews": 4100},
            {"name": "머큐어 앰배서더 서울 홍대", "price": 445000, "rating": 9.0, "reviews": 2800}
        ]
        
        self._save_to_db(results, area_name, checkin_date, nights)
        return len(results)

    def _save_to_db(self, items, area_name, checkin_date, nights):
        db = SessionLocal()
        try:
            for item in items:
                raw_entry = OTAPropertyRaw(
                    ota_source=self.source_name,
                    search_area=area_name,
                    checkin_date=checkin_date,
                    raw_listing_name=item["name"],
                    raw_listing_url=f"https://www.booking.com/searchresults?ss={item['name']}",
                    price_total_krw=item["price"],
                    price_per_night_krw=item["price"] / nights,
                    rating=item["rating"],
                    review_count=item["reviews"],
                    availability_status="available"
                )
                db.add(raw_entry)
            db.commit()
        except Exception as e:
            print(f"Error saving Booking data: {e}")
            db.rollback()
        finally:
            db.close()
