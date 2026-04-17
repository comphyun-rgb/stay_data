import sqlite3
from pathlib import Path

def create_qc_views():
    # Track B DB 경로
    db_path = Path(__file__).parent.parent / "data" / "ota_market.db"
    if not db_path.exists():
        print("Error: Database not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("=== Track B 품질 점검 뷰(QC Views) 생성 시작 ===")

    # 1. OTA별 일반 적재 현황 뷰
    cursor.execute("DROP VIEW IF EXISTS v_ota_summary_stats")
    cursor.execute("""
        CREATE VIEW v_ota_summary_stats AS
        SELECT 
            ota_source,
            COUNT(*) as total_count,
            COUNT(price_total_krw) as price_count,
            COUNT(rating) as rating_count,
            COUNT(raw_lat) as coord_count,
            ROUND(AVG(price_total_krw), 0) as avg_price
        FROM ota_property_raw
        GROUP BY ota_source
    """)

    # 2. 데이터 누락(Doubtful Data) 체크 뷰
    cursor.execute("DROP VIEW IF EXISTS v_ota_data_integrity_issue")
    cursor.execute("""
        CREATE VIEW v_ota_data_integrity_issue AS
        SELECT 
            id, ota_source, raw_listing_name,
            CASE WHEN raw_listing_url IS NULL THEN 'Missing URL'
                 WHEN price_total_krw IS NULL OR price_total_krw = 0 THEN 'Missing Price'
                 WHEN rating IS NULL THEN 'Missing Rating'
                 WHEN raw_lat IS NULL THEN 'Missing Coordinates'
            END as issue_type
        FROM ota_property_raw
        WHERE raw_listing_url IS NULL 
           OR price_total_krw IS NULL OR price_total_krw = 0
           OR rating IS NULL
           OR raw_lat IS NULL
    """)

    # 3. 중복 리스팅 의심 뷰 (동일 URL 기준)
    cursor.execute("DROP VIEW IF EXISTS v_ota_duplicate_candidates")
    cursor.execute("""
        CREATE VIEW v_ota_duplicate_candidates AS
        SELECT raw_listing_url, COUNT(*) as dup_count
        FROM ota_property_raw
        GROUP BY raw_listing_url
        HAVING COUNT(*) > 1
    """)

    conn.commit()
    conn.close()
    print("✅ Quality Control Views created successfully.")

if __name__ == "__main__":
    create_qc_views()
