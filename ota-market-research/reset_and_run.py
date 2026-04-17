import os
from pathlib import Path
from app.db import init_db, DB_PATH, SessionLocal
from scripts.ingest_agoda_pilot import ingest_agoda_harvest
from app.collectors.booking import BookingCollector
from app.collectors.airbnb_manual import AirbnbManualLoader
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
    
    # (1) Agoda 실데이터 (브라우저 수집본)
    ingest_agoda_harvest()
    
    # (2) Booking.com 샘플
    booking = BookingCollector()
    booking.collect_by_area("hongdae")
    
    # (3) Airbnb 수동 샘플
    airbnb = AirbnbManualLoader()
    airbnb_samples = [
        {"name": "연남동 감성 숙소", "price": 180000, "rating": 4.8, "checkin_date": "2026-05-01", "url": "https://airbnb.com/h/yeonnam-sample-1"},
        {"name": "홍대입구역 1분 테라스룸", "price": 125000, "rating": 4.9, "checkin_date": "2026-05-01", "url": "https://airbnb.com/h/hongdae-terrace"}
    ]
    airbnb.ingest_samples(airbnb_samples)
    
    # 3. 품질 점검 리포트 생성
    print("\n--- [Phase 2] QC 리포트 생성 및 분석 ---")
    create_qc_views()
    
    # 4. 스냅샷 적재 검증 (동일 숙소의 시간차 데이터)
    print("\n--- [Phase 3] Snapshot 기능 검증 ---")
    db = SessionLocal()
    try:
        # 첫 번째 리스팅에 대해 가상 스냅샷 1건 추가
        first_raw = db.execute(text("SELECT id, ota_source FROM ota_property_raw LIMIT 1")).fetchone()
        if first_raw:
            snap = OTASnapshot(
                raw_listing_id=first_raw[0],
                ota_source=first_raw[1],
                checkin_date="2026-05-01",
                price_total_krw=415316,
                rating=7.1,
                availability_status="available"
            )
            db.add(snap)
            db.commit()
            print(f"✅ Snapshot 적재 성공 (Raw ID: {first_raw[0]})")

        # 최종 QC 결과 출력
        print("\n[📊 OTA별 수집 통계 리포트]")
        stats = db.execute(text("SELECT * FROM v_ota_summary_stats")).fetchall()
        print(f"{'Source':<15} | {'Count':<6} | {'Price OK':<8} | {'Coord OK':<8} | {'Avg Price':<10}")
        print("-" * 65)
        for row in stats:
            print(f"{row[0]:<15} | {row[1]:<6} | {row[2]:<8} | {row[4]:<8} | {row[5]:<10,.0f}")

    finally:
        db.close()

    print("\n🚀 Track B 홍대 실데이터 파일럿 단계 완료!")

if __name__ == "__main__":
    run_track_b_pilot()
