import sqlite3
import pandas as pd
from pathlib import Path

def check_district_mismatch():
    db_path = "data/seoul_stay.db"
    report_path = "data/exports/district_mismatch_report.csv"
    
    if not Path(db_path).exists():
        print("Error: Database not found.")
        return

    conn = sqlite3.connect(db_path)
    
    print("=== 자치구 정합성 점검 시작 ===")
    
    # district와 district_normalized가 다른 케이스 추출
    query = """
        SELECT 
            id, 
            canonical_name, 
            address_road, 
            district as raw_district, 
            district_normalized as actual_district,
            source_priority
        FROM property_master
        WHERE district != district_normalized
          AND district_normalized != ''
    """
    
    df = pd.read_sql_query(query, conn)
    
    if df.empty:
        print("✅ 모든 데이터의 자치구 정보가 주소와 일치합니다.")
    else:
        print(f"⚠️ 총 {len(df)}건의 자치구 불일치가 발견되었습니다.")
        df.to_csv(report_path, index=False, encoding='utf-8-sig')
        print(f"  └ 리포트 생성 완료: {report_path}")
        
    conn.close()

if __name__ == "__main__":
    check_district_mismatch()
