import sqlite3
import os
from pathlib import Path

def setup_sample_data():
    db_path = Path("data/ota_market.db")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Create Tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ota_property_raw (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ota_source TEXT,
        raw_listing_name TEXT,
        raw_listing_url TEXT,
        price_total_krw FLOAT,
        rating FLOAT,
        review_count INTEGER,
        raw_lat FLOAT,
        raw_lng FLOAT,
        property_type_std TEXT,
        star_rating FLOAT,
        checkin_date TEXT,
        availability_status TEXT DEFAULT 'available'
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ota_room_offer_raw (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        property_raw_id INTEGER,
        ota_source TEXT,
        room_type_name TEXT,
        room_type_std TEXT,
        max_guests INTEGER,
        bed_count INTEGER,
        bed_type_raw TEXT,
        private_bathroom_yn TEXT,
        bathroom_type TEXT,
        cancel_policy_raw TEXT,
        refundable_yn TEXT,
        tax_included_yn TEXT,
        price_total_krw FLOAT,
        FOREIGN KEY(property_raw_id) REFERENCES ota_property_raw(id)
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ota_snapshot (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        property_raw_id INTEGER,
        room_offer_raw_id INTEGER,
        ota_source TEXT,
        price_total_krw FLOAT,
        collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    
    # 2. Insert Sample Data
    # Agoda Samples
    cursor.execute("INSERT INTO ota_property_raw (ota_source, raw_listing_name, price_total_krw, rating, raw_lat, raw_lng, property_type_std, star_rating) VALUES (?,?,?,?,?,?,?,?)", 
                   ('agoda', '호텔 더 디자이너스 홍대', 415316, 7.1, 37.551, 126.920, 'hotel', 3.0))
    p1 = cursor.lastrowid
    cursor.execute("INSERT INTO ota_room_offer_raw (property_raw_id, ota_source, room_type_name, room_type_std, max_guests, private_bathroom_yn, bathroom_type, price_total_krw) VALUES (?,?,?,?,?,?,?,?)",
                   (p1, 'agoda', 'Deluxe Double Room', 'hotel_room', 2, 'Y', 'private', 415316))
    
    cursor.execute("INSERT INTO ota_property_raw (ota_source, raw_listing_name, price_total_krw, rating, raw_lat, raw_lng, property_type_std, star_rating) VALUES (?,?,?,?,?,?,?,?)", 
                   ('agoda', '시스앤브로 게스트하우스', 116349, 7.9, None, None, 'guesthouse', 2.0))
    p2 = cursor.lastrowid
    cursor.execute("INSERT INTO ota_room_offer_raw (property_raw_id, ota_source, room_type_name, room_type_std, max_guests, private_bathroom_yn, bathroom_type, price_total_krw) VALUES (?,?,?,?,?,?,?,?)",
                   (p2, 'agoda', 'Single Bed in 6-Bed Dorm', 'dorm_bed', 1, 'N', 'shared', 25000))
    cursor.execute("INSERT INTO ota_room_offer_raw (property_raw_id, ota_source, room_type_name, room_type_std, max_guests, private_bathroom_yn, bathroom_type, price_total_krw) VALUES (?,?,?,?,?,?,?,?)",
                   (p2, 'agoda', 'Standard Double Room', 'private_room', 2, 'Y', 'private', 116349))

    # Booking.com Samples
    cursor.execute("INSERT INTO ota_property_raw (ota_source, raw_listing_name, price_total_krw, rating, raw_lat, raw_lng, property_type_std, star_rating) VALUES (?,?,?,?,?,?,?,?)", 
                   ('booking_com', '나인 브릭 호텔', 483511, 8.7, 37.554, 126.921, 'hotel', 4.0))
    p3 = cursor.lastrowid
    cursor.execute("INSERT INTO ota_room_offer_raw (property_raw_id, ota_source, room_type_name, room_type_std, max_guests, private_bathroom_yn, bathroom_type, price_total_krw) VALUES (?,?,?,?,?,?,?,?)",
                   (p3, 'booking_com', 'Superior Double', 'hotel_room', 2, 'Y', 'private', 483511))

    # Airbnb Samples
    cursor.execute("INSERT INTO ota_property_raw (ota_source, raw_listing_name, price_total_krw, rating, raw_lat, raw_lng, property_type_std) VALUES (?,?,?,?,?,?,?)", 
                   ('airbnb', '연남동 감성 숙소', 180000, 4.8, 37.560, 126.924, 'apartment'))
    p4 = cursor.lastrowid
    cursor.execute("INSERT INTO ota_room_offer_raw (property_raw_id, ota_source, room_type_name, room_type_std, max_guests, private_bathroom_yn, bathroom_type, price_total_krw) VALUES (?,?,?,?,?,?,?,?)",
                   (p4, 'airbnb', '전체 공간', 'private_room', 2, 'Y', 'private', 180000))

    # 3. Snapshots
    cursor.execute("INSERT INTO ota_snapshot (property_raw_id, room_offer_raw_id, ota_source, price_total_krw) VALUES (?,?,?,?)", (p1, 1, 'agoda', 415316))
    
    conn.commit()
    conn.close()
    print("DONE: Sample data loaded into ota_market.db")

def run_audit():
    db_path = Path("data/ota_market.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n--- [1] Record Counts ---")
    cursor.execute("SELECT ota_source, COUNT(*) FROM ota_property_raw GROUP BY ota_source")
    print("Property Raw Counts:", cursor.fetchall())
    cursor.execute("SELECT ota_source, COUNT(*) FROM ota_room_offer_raw GROUP BY ota_source")
    print("Room Offer Counts:", cursor.fetchall())
    cursor.execute("SELECT ota_source, COUNT(*) FROM ota_snapshot GROUP BY ota_source")
    print("Snapshot Counts:", cursor.fetchall())
    
    print("\n--- [2] Fill Rate & Null Ratio ---")
    fields = ['room_type_name', 'room_type_std', 'max_guests', 'bed_count', 'bed_type_raw', 'private_bathroom_yn', 'bathroom_type', 'refundable_yn', 'tax_included_yn']
    for field in fields:
        cursor.execute(f"SELECT ota_source, COUNT({field}), COUNT(*) FROM ota_room_offer_raw GROUP BY ota_source")
        res = cursor.fetchall()
        print(f"Fill Rate [{field}]:", [(r[0], f"{r[1]}/{r[2]} ({r[1]/r[2]*100:.1f}%)") for r in res])
        
    print("\n--- [3] Standardization Samples ---")
    cursor.execute("SELECT ota_source, room_type_name, room_type_std, bathroom_type, max_guests FROM ota_room_offer_raw LIMIT 5")
    samples = cursor.fetchall()
    print("Samples (Source | Room Name | Std | Bathroom | Max Guests):")
    for s in samples:
        print(s)
        
    print("\n--- [4] Price Data Audit ---")
    cursor.execute("SELECT COUNT(*) FROM ota_property_raw WHERE price_total_krw IS NULL OR price_total_krw = 0")
    print("Zero/Null Price Count:", cursor.fetchone()[0])
    cursor.execute("SELECT * FROM ota_property_raw WHERE price_total_krw > 1000000 OR price_total_krw < 10000")
    print("Price Outliers:", cursor.fetchall())
    
    print("\n--- [5] Coordinate Fill Rate ---")
    cursor.execute("SELECT ota_source, COUNT(raw_lat), COUNT(*) FROM ota_property_raw GROUP BY ota_source")
    res = cursor.fetchall()
    print("Coordinate Fill Rate:", [(r[0], f"{r[1]}/{r[2]}") for r in res])
    
    conn.close()

if __name__ == "__main__":
    setup_sample_data()
    run_audit()
