import pandas as pd
from pathlib import Path
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models.property_entity import PropertyEntity
from app.models.ota_listing_map import OTAMapping
from app.models.ota_snapshot import OTASnapshot
from datetime import datetime

def import_ota_pilot_data(csv_path: str):
    if not Path(csv_path).exists():
        print(f"Error: File not found at {csv_path}")
        return

    db: Session = SessionLocal()
    try:
        df = pd.read_csv(csv_path)
        print(f"\n=== OTA 파일럿 데이터 임포트 시작 ({len(df)}건) ===")
        
        success_map = 0
        success_snap = 0
        
        for index, row in df.iterrows():
            # 필수 값 체크
            if pd.isna(row['raw_listing_url']) or pd.isna(row['ota_source']):
                continue
            
            # 1. ota_listing_map 처리 (기존 매핑 확인 또는 신규 생성)
            mapping = db.query(OTAMapping).filter(
                OTAMapping.ota_source == row['ota_source'],
                OTAMapping.raw_listing_url == row['raw_listing_url']
            ).first()
            
            if not mapping:
                mapping = OTAMapping(
                    property_entity_id=int(row['property_entity_id']),
                    ota_source=row['ota_source'],
                    raw_listing_name=row['raw_listing_name'],
                    raw_listing_url=row['raw_listing_url'],
                    match_status='matched',
                    verified_by='pilot_researcher',
                    verified_at=datetime.now()
                )
                db.add(mapping)
                db.flush() # mapping.id 확보
                success_map += 1
            
            # 2. ota_snapshot 처리 (새로운 가격/평점 정보 적재)
            # 가격 정보가 있는 경우에만 적재
            if not pd.isna(row['price_total_krw']):
                snapshot = OTASnapshot(
                    ota_listing_map_id=mapping.id,
                    property_entity_id=mapping.property_entity_id,
                    ota_source=mapping.ota_source,
                    checkin_date=str(row['checkin_date']),
                    price_total_krw=float(row['price_total_krw']),
                    price_per_night_krw=float(row['price_total_krw']) / int(row.get('nights', 1)),
                    rating=float(row['rating']) if not pd.isna(row['rating']) else None,
                    review_count=int(row['review_count']) if not pd.isna(row['review_count']) else None,
                    room_type=row.get('room_type'),
                    refundable_yn=row.get('refundable_yn'),
                    breakfast_yn=row.get('breakfast_yn'),
                    availability_status=row.get('availability_status', 'available'),
                    raw_listing_name=row['raw_listing_name'],
                    raw_listing_url=row['raw_listing_url']
                )
                db.add(snapshot)
                success_snap += 1
        
        db.commit()
        print(f"✅ 임포트 완료!")
        print(f"   - 신규 매핑 등록: {success_map}건")
        print(f"   - 가격 스냅샷 적재: {success_snap}건")
        
    except Exception as e:
        print(f"❌ 임포트 중 오류 발생: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # 실행 예시: python3 scripts/import_ota_pilot_data.py
    # 실제 운영 시 파일 경로를 인자로 받거나 지정된 경로 사용
    target_csv = "data/exports/hongdae_pilot_research_list.csv" # 조사 완료된 파일 경로
    import_ota_pilot_data(target_csv)
