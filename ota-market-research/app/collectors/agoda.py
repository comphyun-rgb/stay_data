import requests
from datetime import datetime, timedelta
from app.models.ota_property_raw import OTAPropertyRaw
from app.db import SessionLocal

class AgodaCollector:
    """
    Agoda 지역 검색 결과 기반 리스팅 수집기.
    홍대권 등의 특정 지역 키워드로 검색하여 상위 노출 숙소 정보를 가져옴.
    """
    def __init__(self):
        self.source_name = "agoda"
        self.base_url = "https://www.agoda.com" # 실제 구현 시 API 또는 스크레이핑 엔진 연결

    def collect_by_area(self, area_name: str, checkin_offset: int = 14, nights: int = 1):
        """
        특정 지역 명칭으로 검색하여 리스팅을 수집함.
        """
        checkin_date = (datetime.now() + timedelta(days=checkin_offset)).strftime("%Y-%m-%d")
        print(f"[{self.source_name}] '{area_name}' 지역 수집 시작 (Check-in: {checkin_date})")
        
        # [실제 수집 로직 위치]
        # 이 부분에 브라우저 자동화 또는 AJAX API 호출 로직이 들어감.
        # 파일럿용으로 구조만 먼저 설계함.
        
        results = []
        # Mock Data 예시 (파일럿 구동 확인용)
        mock_data = {
            "raw_listing_name": "호텔 더 디자이너스 홍대",
            "raw_listing_url": "https://www.agoda.com/hotel-the-designers-hongdae",
            "price_total_krw": 457992,
            "rating": 7.1,
            "review_count": 7750,
            "availability_status": "available"
        }
        results.append(mock_data)
        
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
                    nights=nights,
                    raw_listing_name=item["raw_listing_name"],
                    raw_listing_url=item["raw_listing_url"],
                    price_total_krw=item["price_total_krw"],
                    price_per_night_krw=item["price_total_krw"] / nights,
                    rating=item["rating"],
                    review_count=item["review_count"],
                    availability_status=item["availability_status"]
                )
                db.add(raw_entry)
            db.commit()
        except Exception as e:
            print(f"Error saving Agoda data: {e}")
            db.rollback()
        finally:
            db.close()
