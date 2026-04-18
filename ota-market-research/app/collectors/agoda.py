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

    def collect_by_area(self, area_name: str, keyword: str = None, checkin_offset: int = 14, nights: int = 1):
        """
        특정 지역 명칭 및 키워드로 검색하여 리스팅을 수집함.
        """
        search_keyword = keyword or area_name
        checkin_date = (datetime.now() + timedelta(days=checkin_offset)).strftime("%Y-%m-%d")
        print(f"[{self.source_name}] 키워드 '{search_keyword}' 수집 시작 (Check-in: {checkin_date})")
        
        # [실제 수집 로직 위치]
        # 이 부분에 브라우저 자동화 또는 AJAX API 호출 로직이 들어감.
        # 파일럿용으로 구조만 먼저 설계함.
        
        results = []
        # Mock Data (Property + Rooms)
        mock_data = {
            "name": "호텔 더 디자이너스 홍대",
            "url": "https://www.agoda.com/hotel-the-designers-hongdae",
            "lat": 37.5512, "lng": 126.9201,
            "property_type": "Hotel",
            "star_rating": 3.0,
            "rooms": [
                {
                    "name": "Deluxe Double", "price": 457992, "guests": "2 adults",
                    "bathroom": "Private Bathroom", "policy": "Free Cancellation", "tax": "Tax Included"
                },
                {
                    "name": "Superior Twin", "price": 489000, "guests": "2 adults",
                    "bathroom": "Private Bathroom", "policy": "Non-refundable", "tax": "Tax Included"
                }
            ]
        }
        results.append(mock_data)
        
        self._save_to_db(results, area_name, search_keyword, checkin_date, nights)
        return len(results)

    def _save_to_db(self, items, area_name, search_keyword, checkin_date, nights):
        db = SessionLocal()
        parser = OTAParser()
        try:
            for item in items:
                # 1. Property 저장 (또는 기존 정보 업데이트)
                # URL 또는 OTA ID 기준 중복 체크
                prop = db.query(OTAPropertyRaw).filter(
                    (OTAPropertyRaw.raw_listing_url == item["url"]) | 
                    (OTAPropertyRaw.raw_listing_id == item.get("id"))
                ).first()
                
                if not prop:
                    prop = OTAPropertyRaw(
                        ota_source=self.source_name,
                        search_area=area_name,
                        search_keyword=search_keyword,
                        raw_listing_name=item["name"],
                        raw_listing_url=item["url"],
                        raw_listing_id=item.get("id"),
                        raw_lat=item.get("lat"),
                        raw_lng=item.get("lng"),
                        property_type_raw=item.get("property_type"),
                        property_type_std=parser.parse_room_type(item.get("property_type", "")),
                        star_rating=item.get("star_rating")
                    )
                    db.add(prop)
                    db.flush()
                else:
                    # 기존 정보 업데이트 (좌표 보강 등)
                    if not prop.raw_lat and item.get("lat"): prop.raw_lat = item["lat"]
                    if not prop.raw_lng and item.get("lng"): prop.raw_lng = item["lng"]
                    if not prop.search_keyword: prop.search_keyword = search_keyword
                
                # 2. Rooms/Offers 저장
                for r in item.get("rooms", []):
                    # 기존 동일 상품 확인 (ID 등 고유 식별자 없을 시 이름+가격으로 임시 매칭)
                    offer = OTARoomOfferRaw(
                        property_raw_id=prop.id,
                        ota_source=self.source_name,
                        room_type_name=r["name"],
                        room_type_std=parser.parse_room_type(r["name"]),
                        max_guests=parser.parse_max_guests(r["guests"]),
                        private_bathroom_yn=parser.parse_bathroom_type(r["bathroom"])[0],
                        bathroom_type=parser.parse_bathroom_type(r["bathroom"])[1],
                        cancel_policy_raw=r["policy"],
                        refundable_yn=parser.parse_refundable(r["policy"]),
                        tax_included_yn=parser.parse_tax_included(r["tax"]),
                        price_total_krw=r["price"],
                        price_per_night_krw=r["price"] / nights
                    )
                    db.add(offer)
                    db.flush()

                    # 3. Snapshot 누적
                    snap = OTASnapshot(
                        property_raw_id=prop.id,
                        room_offer_raw_id=offer.id,
                        ota_source=self.source_name,
                        room_type_name=r["name"],
                        checkin_date=checkin_date,
                        price_total_krw=r["price"],
                        price_per_night_krw=r["price"] / nights,
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
