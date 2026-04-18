import os
from pathlib import Path
from app.db import init_db, DB_PATH, SessionLocal
from app.collectors.agoda import AgodaCollector
from app.collectors.booking import BookingCollector
from app.collectors.airbnb_manual import AirbnbManualLoader
from scripts.bulk_harvest_hongdae import run_bulk_harvest
from scripts.create_qc_reports import create_qc_views
from app.models.ota_property_entity import OTASnapshot
from sqlalchemy import text

def run_track_b_pilot():
    print("\n=== [Track B] 홍대권 실데이터 적재 파일럿 시작 ===")
    
    # 1. DB 초기화
    if DB_PATH.exists(): os.remove(DB_PATH)
    init_db()
    
    # 2. 채널별 데이터 적재
    print("\n--- [Phase 1] 다채널 데이터 수집 및 적재 ---")
    
    # (1) Bulk 하베스팅 (100+ 숙소 확보)
    run_bulk_harvest()
    
    # (2) Airbnb 수동 샘플
    airbnb = AirbnbManualLoader()
    airbnb_samples = [
        {"name": "연남동 감성 숙소", "price": 180000, "rating": 4.8, "checkin_date": "2026-05-01", "url": "https://airbnb.com/h/yeonnam-sample-1", "lat": 37.560, "lng": 126.924},
        {"name": "홍대입구역 1분 테라스룸", "price": 125000, "rating": 4.9, "checkin_date": "2026-05-01", "url": "https://airbnb.com/h/hongdae-terrace", "lat": 37.558, "lng": 126.922}
    ]
    airbnb.ingest_samples(airbnb_samples)
    
    # 3. 품질 점검 리포트 생성
    print("\n--- [Phase 2] QC 리포트 생성 및 분석 ---")
    create_qc_views()
    
    # 4. 운영용 스크립트 실행 (Audit & Report)
    print("\n--- [Phase 3] 운영용 점검 스크립트 검증 ---")
    from scripts.run_audit import run_audit
    from scripts.generate_qc_report import generate_report
    
    run_audit()
    generate_report()

    print("\n🚀 Track B 홍대 실데이터 파일럿 단계 완료!")

if __name__ == "__main__":
    run_track_b_pilot()
