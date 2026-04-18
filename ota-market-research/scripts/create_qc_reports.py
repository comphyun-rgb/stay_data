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
            COUNT(property_type_std) as property_std_count,
            ROUND(AVG(price_total_krw), 0) as avg_price
        FROM ota_property_raw
        GROUP BY ota_source
    """)

    # 2. 객실/상품 데이터 충전율 점검 뷰
    cursor.execute("DROP VIEW IF EXISTS v_ota_room_offer_fill_rate")
    cursor.execute("""
        CREATE VIEW v_ota_room_offer_fill_rate AS
        SELECT 
            ota_source,
            COUNT(*) as total_count,
            COUNT(room_type_name) as room_name_count,
            COUNT(room_type_std) as room_std_count,
            COUNT(max_guests) as guests_count,
            COUNT(bed_count) as bed_count_count,
            COUNT(bed_type_raw) as bed_raw_count,
            COUNT(private_bathroom_yn) as bathroom_yn_count,
            COUNT(bathroom_type) as bathroom_type_count,
            COUNT(cancel_policy_raw) as cancel_count,
            COUNT(tax_included_yn) as tax_count,
            COUNT(refundable_yn) as refund_count
        FROM ota_room_offer_raw
        GROUP BY ota_source
    """)

    # 3. 표준화 품질 점검 (분포 및 Unknown 비율)
    cursor.execute("DROP VIEW IF EXISTS v_ota_standardization_dist")
    cursor.execute("""
        CREATE VIEW v_ota_standardization_dist AS
        SELECT 'property_type_std' as field, property_type_std as value, COUNT(*) as count
        FROM ota_property_raw GROUP BY property_type_std
        UNION ALL
        SELECT 'room_type_std' as field, room_type_std as value, COUNT(*) as count
        FROM ota_room_offer_raw GROUP BY room_type_std
        UNION ALL
        SELECT 'bathroom_type' as field, bathroom_type as value, COUNT(*) as count
        FROM ota_room_offer_raw GROUP BY bathroom_type
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

    # 4. 키워드별 수집 분포 뷰
    cursor.execute("DROP VIEW IF EXISTS v_ota_keyword_distribution")
    cursor.execute("""
        CREATE VIEW v_ota_keyword_distribution AS
        SELECT search_keyword, COUNT(*) as property_count
        FROM ota_property_raw
        GROUP BY search_keyword
    """)

    conn.commit()
    conn.close()
    print("DONE: Quality Control Views created successfully.")

if __name__ == "__main__":
    create_qc_views()
