from datetime import datetime, timedelta
from app.models.ota_property_raw import OTAPropertyRaw
from app.models.ota_room_offer_raw import OTARoomOfferRaw
from app.models.ota_property_entity import OTASnapshot
from app.db import SessionLocal
from app.utils.parser import OTAParser

class BookingCollector:
    """
    Booking.com 지역 검색 결과 기반 리스팅 수집기.
    """
    def __init__(self):
        self.source_name = "booking_com"

    def collect_by_area(self, area_name: str, keyword: str = None, checkin_offset: int = 14, nights: int = 1):
        search_keyword = keyword or area_name
        checkin_date = (datetime.now() + timedelta(days=checkin_offset)).strftime("%Y-%m-%d")
        print(f"[{self.source_name}] 키워드 '{search_keyword}' 샘플 수집 시작")
        
        # [실제 수집 시엔 Booking.com 검색 결과 파싱 로직 포함]
        results = [
            {
                "name": "L7 홍대 바이 롯데", "price": 385000, "rating": 8.7, "reviews": 3200,
                "url": "https://www.booking.com/hotel/kr/l7-hongdae",
                "lat": 37.5545, "lng": 126.9215,
                "rooms": [
                    {"name": "Standard Double", "price": 385000, "guests": "2인", "bathroom": "전용 욕실", "policy": "무료 취소", "tax": "세금 포함"}
                ]
            },
            {
                "name": "머큐어 앰배서더 서울 홍대", "price": 445000, "rating": 9.0, "reviews": 2800,
                "url": "https://www.booking.com/hotel/kr/mercure-hongdae",
                "lat": 37.5552, "lng": 126.9208,
                "rooms": [
                    {"name": "Superior King", "price": 445000, "guests": "2인", "bathroom": "전용 욕실", "policy": "취소 불가", "tax": "세금 포함"}
                ]
            }
        ]
        
        self._save_to_db(results, area_name, search_keyword, checkin_date, nights)
        return len(results)

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
                        raw_lat=item.get("lat"),
                        raw_lng=item.get("lng"),
                        rating=item.get("rating")
                    )
                    db.add(prop)
                    db.flush()
                else:
                    if not prop.raw_lat and item.get("lat"): prop.raw_lat = item["lat"]
                    if not prop.search_keyword: prop.search_keyword = search_keyword
                
                # 2. Rooms
                for r in item.get("rooms", []):
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

                    # 3. Snapshot
                    snap = OTASnapshot(
                        property_raw_id=prop.id,
                        room_offer_raw_id=offer.id,
                        ota_source=self.source_name,
                        room_type_name=r["name"],
                        checkin_date=checkin_date,
                        price_total_krw=r["price"],
                        price_per_night_krw=r["price"] / nights
                    )
                    db.add(snap)
            
            db.commit()
            print(f"DONE: [{self.source_name}] Property/Room/Snapshot 적재 완료")
        except Exception as e:
            print(f"Error saving Booking data: {e}")
            db.rollback()
        finally:
            db.close()
