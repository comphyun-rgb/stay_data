import sqlite3
from pathlib import Path

def create_views():
    db_path = "data/seoul_stay.db"
    if not Path(db_path).exists():
        print("Error: Database not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # --- [1] 엔티티 기초 뷰 ---
    cursor.execute("DROP VIEW IF EXISTS v_entity_curated")
    cursor.execute("""
        CREATE VIEW v_entity_curated AS
        SELECT 
            e.id as entity_id,
            e.display_name,
            e.representative_address,
            e.district,
            e.cluster_area,
            e.lat,
            e.lng,
            e.master_count,
            (SELECT COUNT(*) FROM property_master m 
             WHERE m.entity_id = e.id AND m.status_std = 'active') as active_master_count
        FROM property_entity e
    """)

    # --- [2] 홍대 파일럿 타깃 뷰 (PILOT ONLY) ---
    cursor.execute("DROP VIEW IF EXISTS v_hongdae_active_target")
    cursor.execute("""
        CREATE VIEW v_hongdae_active_target AS
        SELECT * FROM v_entity_curated
        WHERE cluster_area = '홍대권'
          AND active_master_count > 0
          AND lat IS NOT NULL AND lng IS NOT NULL
    """)

    # --- [3] 홍대 파일럿 매핑 현황 뷰 (QC) ---
    cursor.execute("DROP VIEW IF EXISTS v_hongdae_mapping_status")
    cursor.execute("""
        CREATE VIEW v_hongdae_mapping_status AS
        SELECT 
            h.entity_id,
            h.display_name,
            (SELECT COUNT(*) FROM ota_listing_map m WHERE m.property_entity_id = h.entity_id AND m.ota_source = 'agoda') as has_agoda,
            (SELECT COUNT(*) FROM ota_listing_map m WHERE m.property_entity_id = h.entity_id AND m.ota_source = 'booking_com') as has_booking,
            (SELECT COUNT(*) FROM ota_listing_map m WHERE m.property_entity_id = h.entity_id AND m.ota_source = 'airbnb') as has_airbnb,
            (SELECT COUNT(*) FROM ota_listing_map m WHERE m.property_entity_id = h.entity_id) as total_listings
        FROM v_hongdae_active_target h
    """)

    # --- [4] 홍대 파일럿 최신 스냅샷 뷰 (Price Check) ---
    cursor.execute("DROP VIEW IF EXISTS v_hongdae_snapshot_recent")
    cursor.execute("""
        CREATE VIEW v_hongdae_snapshot_recent AS
        SELECT 
            s.id as snapshot_id,
            e.display_name,
            s.ota_source,
            s.checkin_date,
            s.price_total_krw,
            s.rating,
            s.review_count,
            s.room_type,
            s.collected_at
        FROM ota_snapshot s
        JOIN property_entity e ON s.property_entity_id = e.id
        WHERE e.cluster_area = '홍대권'
        ORDER BY s.collected_at DESC
    """)

    conn.commit()
    conn.close()
    print("✅ Hongdae Pilot Operational Views created successfully.")

if __name__ == "__main__":
    create_views()
