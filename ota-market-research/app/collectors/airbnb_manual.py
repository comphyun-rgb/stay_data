from app.models.ota_property_raw import OTAPropertyRaw
from app.db import SessionLocal

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
        try:
            print(f"[{self.source_name}] 수동 샘플 {len(samples_list)}건 적재 시작")
            for item in samples_list:
                raw_entry = OTAPropertyRaw(
                    ota_source=self.source_name,
                    search_area=item.get("search_area", "hongdae"),
                    checkin_date=item.get("checkin_date"),
                    raw_listing_name=item["name"],
                    raw_listing_url=item.get("url"),
                    price_total_krw=item.get("price"),
                    rating=item.get("rating"),
                    review_count=item.get("review_count"),
                    availability_status="available"
                )
                db.add(raw_entry)
            db.commit()
            print(f"✅ {self.source_name} 샘플 적재 완료")
        except Exception as e:
            print(f"Error loading Airbnb samples: {e}")
            db.rollback()
        finally:
            db.close()
