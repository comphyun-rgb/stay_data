import sqlite3
from pathlib import Path

def generate_report():
    db_path = Path(__file__).parent.parent / "data" / "ota_market.db"
    if not db_path.exists():
        print(f"Error: Database not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n=== [Track B] QC 분석 리포트 생성 ===")
    
    views = [
        "v_ota_summary_stats",
        "v_ota_room_offer_fill_rate",
        "v_ota_standardization_dist",
        "v_ota_data_integrity_issue"
    ]
    
    for view in views:
        print(f"\n[View: {view}]")
        try:
            cursor.execute(f"SELECT * FROM {view}")
            cols = [description[0] for description in cursor.description]
            print(" | ".join(cols))
            print("-" * (len(cols) * 15))
            for row in cursor.fetchall():
                print(" | ".join(str(val) for val in row))
        except Exception as e:
            print(f"Error reading view {view}: {e}")

    conn.close()

if __name__ == "__main__":
    generate_report()
