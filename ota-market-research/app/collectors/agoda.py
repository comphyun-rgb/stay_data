import requests
from datetime import datetime, timedelta
from app.models.ota_property_raw import OTAPropertyRaw
from app.models.ota_room_offer_raw import OTARoomOfferRaw
from app.models.ota_property_entity import OTASnapshot
from app.db import SessionLocal
from app.utils.parser import OTAParser

class AgodaCollector:
    """
    Agoda 지역 검색 결과 기반 리스팅 수집기.
    홍대권 등의 특정 지역 키워드로 검색하여 상위 노출 숙소 정보를 가져옴.
    """
    def __init__(self):
        self.source_name = "agoda"
        self.base_url = "https://www.agoda.com" # 실제 구현 시 API 또는 스크레이핑 엔진 연결

    def collect_by_area(self, area_name: str, keyword: str = None, checkin_offset: int = 14, nights: int = 1, pages: int = 1):
        """
        특정 지역 명칭 및 키워드로 검색하여 리스팅을 수집함 (페이지네이션 지원).
        """
        search_keyword = keyword or area_name
        checkin_date = (datetime.now() + timedelta(days=checkin_offset)).strftime("%Y-%m-%d")
        print(f"[{self.source_name}] 키워드 '{search_keyword}' 수집 시작 (Check-in: {checkin_date}, Pages: {pages})")
        
        for p in range(1, pages + 1):
            print(f"  - [{self.source_name}] {p}페이지 수집 중...")
            # [실제 페이지별 수집 로직]
            results = self._mock_search_results(p, area_name) # Area-specific mock
            self._save_to_db(results, area_name, search_keyword, checkin_date, nights)

    def _mock_search_results(self, page, area):
        # Generate region-specific results to avoid URL conflicts
        area_id = area.lower().replace("-", "")
        return [
            {
                "name": f"{area} Hotel {page}A", "url": f"https://www.agoda.com/h/{area_id}_{page}a",
                "lat": 37.551, "lng": 126.920, "rating": 8.5, "review_count": 100 * page,
                "rooms": [{"name": "Standard Double", "price": 100000 + (page*5000), "guests": "2 adults", "bathroom": "Private", "policy": "Free"}]
            },
            {
                "name": f"{area} Hostel {page}B", "url": f"https://www.agoda.com/h/{area_id}_{page}b",
                "lat": 37.552, "lng": 126.921, "rating": 7.5, "review_count": 50 * page,
                "rooms": [{"name": "Bed in 6-Dorm", "price": 30000 + (page*2000), "guests": "1 adult", "bathroom": "Shared", "policy": "Non"}]
            }
        ]

    def _save_to_db(self, items, area_name, search_keyword, checkin_date, nights):
        db = SessionLocal()
        parser = OTAParser()
        try:
            for item in items:
                # 1. Property
                prop = db.query(OTAPropertyRaw).filter_by(raw_listing_url=item["url"]).first()
                if not prop:
                    prop = OTAPropertyRaw(
                        ota_source=self.source_name,
                        search_area=area_name,
                        search_keyword=search_keyword,
                        raw_listing_name=item["name"],
                        raw_listing_url=item["url"],
                        raw_address=item.get("address"),
                        raw_lat=item.get("lat"),
                        raw_lng=item.get("lng"),
                        rating=item.get("rating"),
                        review_count=item.get("review_count")
                    )
                    db.add(prop)
                    db.flush()
                
                # 2. Rooms/Offers
                for r in item.get("rooms", []):
                    max_guests = parser.parse_max_guests(r["guests"])
                    offer = OTARoomOfferRaw(
                        property_raw_id=prop.id,
                        ota_source=self.source_name,
                        room_type_name=r["name"],
                        room_type_std=parser.parse_room_type(r["name"]),
                        analysis_unit=parser.classify_analysis_unit(r["name"], max_guests),
                        max_guests=max_guests,
                        private_bathroom_yn=parser.parse_bathroom_type(r["bathroom"])[0],
                        bathroom_type=parser.parse_bathroom_type(r["bathroom"])[1],
                        cancel_policy_raw=r["policy"],
                        refundable_yn=parser.parse_refundable(r["policy"]),
                        tax_included_yn=parser.parse_tax_included(r.get("tax", "included")),
                        price_total_krw=r["price"],
                        price_per_night_krw=r["price"] / nights
                    )
                    db.add(offer)
                    db.flush()

                    # 3. Snapshot
                    snap = OTASnapshot(
                        property_raw_id=prop.id,
                        room_offer_raw_id=offer.id,
                        ota_source=self.source_name,
                        room_type_name=r["name"],
                        checkin_date=checkin_date,
                        price_total_krw=r["price"],
                        price_per_night_krw=r["price"] / nights,
                        rating=item.get("rating"),
                        review_count=item.get("review_count"),
                        availability_status="available"
                    )
                    db.add(snap)
            db.commit()
            print(f"DONE: [{self.source_name}] Property/Room/Snapshot 적재 완료")
        except Exception as e:
            print(f"Error saving Agoda data: {e}")
            db.rollback()
        finally:
            db.close()
