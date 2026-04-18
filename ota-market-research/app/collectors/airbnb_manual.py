from app.models.ota_property_raw import OTAPropertyRaw
from app.models.ota_room_offer_raw import OTARoomOfferRaw
from app.models.ota_property_entity import OTASnapshot
from app.db import SessionLocal
from app.utils.parser import OTAParser

class AirbnbManualLoader:
    """
    Airbnb 숙소 리스트를 수동/반수동으로 적재하는 로더.
    """
    def __init__(self):
        self.source_name = "airbnb"

    def ingest_samples(self, samples_list):
        """
        외부에서 정리된 샘플 리스트를 받아 적재함.
        """
        db = SessionLocal()
        parser = OTAParser()
        try:
            print(f"[{self.source_name}] 수동 샘플 {len(samples_list)}건 적재 시작")
            for item in samples_list:
                # 1. Property
                prop = OTAPropertyRaw(
                    ota_source=self.source_name,
                    search_area=item.get("search_area", "hongdae"),
                    raw_listing_name=item["name"],
                    raw_listing_url=item.get("url"),
                    raw_lat=item.get("lat"),
                    raw_lng=item.get("lng"),
                    rating=item.get("rating")
                )
                db.add(prop)
                db.flush()

                # 2. Room/Offer (Airbnb는 기본적으로 숙소=객실이나 구조 통일)
                offer = OTARoomOfferRaw(
                    property_raw_id=prop.id,
                    ota_source=self.source_name,
                    room_type_name="Entire Place" if not item.get("room_type") else item["room_type"],
                    room_type_std=parser.parse_room_type(item.get("room_type", "entire")),
                    max_guests=item.get("max_guests", 2),
                    private_bathroom_yn="Y", # Airbnb 전체공간 기준
                    bathroom_type="private",
                    price_total_krw=item.get("price"),
                    price_per_night_krw=item.get("price")
                )
                db.add(offer)
                db.flush()

                # 3. Snapshot
                snap = OTASnapshot(
                    property_raw_id=prop.id,
                    room_offer_raw_id=offer.id,
                    ota_source=self.source_name,
                    room_type_name=offer.room_type_name,
                    checkin_date=item.get("checkin_date"),
                    price_total_krw=item.get("price"),
                    price_per_night_krw=item.get("price")
                )
                db.add(snap)
            
            db.commit()
            print(f"DONE: {self.source_name} 샘플 적재 완료")
        except Exception as e:
            print(f"Error loading Airbnb samples: {e}")
            db.rollback()
        finally:
            db.close()
