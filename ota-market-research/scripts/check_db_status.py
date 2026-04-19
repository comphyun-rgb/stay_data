import sys
import os
from sqlalchemy import text

# Add root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal

def check_db():
    db = SessionLocal()
    tables = [
        'ota_property_raw', 
        'ota_room_offer_raw', 
        'ota_snapshot', 
        'ota_property_entity', 
        'ota_coordinate_validation', 
        'ota_manual_match'
    ]
    
    print("\n=== [DATABASE TABLE STATUS] ===")
    print(f"{'Table Name':<30} | {'Row Count':<10} | {'Status'}")
    print("-" * 55)
    
    for table in tables:
        try:
            count = db.execute(text(f"SELECT count(*) FROM {table}")).scalar()
            status = "ACTIVE" if count > 0 else "EMPTY (Pending Process)"
            print(f"{table:<30} | {count:<10} | {status}")
        except Exception as e:
            print(f"{table:<30} | {'Error':<10} | {str(e)[:20]}...")
            
    db.close()

if __name__ == "__main__":
    check_db()
