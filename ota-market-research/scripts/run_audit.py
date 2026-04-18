import sqlite3
from pathlib import Path

def run_audit():
    db_path = Path(__file__).parent.parent / "data" / "ota_market.db"
    if not db_path.exists():
        print(f"Error: Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n=== [Track B] 데이터 적재 및 품질 현황 점검 ===")
    
    # 1. 레코드 건수 확인
    print("\n[1] 레코드 건수 (Records Count)")
    cursor.execute("SELECT ota_source, COUNT(*) FROM ota_property_raw GROUP BY ota_source")
    print("Property Raw:", cursor.fetchall())
    cursor.execute("SELECT ota_source, COUNT(*) FROM ota_room_offer_raw GROUP BY ota_source")
    print("Room Offer:", cursor.fetchall())
    cursor.execute("SELECT ota_source, COUNT(*) FROM ota_snapshot GROUP BY ota_source")
    print("Snapshot (Time-series):", cursor.fetchall())
    
    # 2. 핵심 필드 충전율 (Fill Rate)
    print("\n[2] 주요 필드 보유율 (Fill Rate)")
    fields = ['raw_lat', 'raw_lng', 'room_type_std', 'max_guests', 'private_bathroom_yn', 'refundable_yn', 'tax_included_yn']
    # Property level
    cursor.execute("SELECT ota_source, COUNT(raw_lat), COUNT(*) FROM ota_property_raw GROUP BY ota_source")
    print(f"Fill Rate [Coordinates]:", cursor.fetchall())
    
    # Room level
    for field in ['room_type_std', 'max_guests', 'private_bathroom_yn', 'refundable_yn']:
        cursor.execute(f"SELECT ota_source, COUNT({field}), COUNT(*) FROM ota_room_offer_raw GROUP BY ota_source")
        print(f"Fill Rate [{field}]:", cursor.fetchall())
        
    # 3. 표준화 품질 샘플
    print("\n[3] 표준화 매핑 샘플 (Standardization Samples)")
    cursor.execute("""
        SELECT ota_source, room_type_name, room_type_std, max_guests, bathroom_type 
        FROM ota_room_offer_raw LIMIT 5
    """)
    print("Samples:", cursor.fetchall())
    
    # 4. 가격 이상치 점검
    print("\n[4] 가격 데이터 이상치 점검 (Price Outliers)")
    cursor.execute("SELECT ota_source, raw_listing_name, price_total_krw FROM ota_property_raw WHERE price_total_krw > 1000000 OR price_total_krw < 10000")
    print("Outliers (>1M or <10K):", cursor.fetchall())

    conn.close()
    print("\n점검 완료.")

if __name__ == "__main__":
    run_audit()
