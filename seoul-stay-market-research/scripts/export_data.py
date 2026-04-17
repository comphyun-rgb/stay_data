import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime

def export_full_data():
    db_path = "data/seoul_stay.db"
    export_path = "data/exports/property_master_full.csv"
    
    if not Path(db_path).exists():
        print(f"[ERROR] Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    
    try:
        # DB의 모든 데이터를 읽어옴 (raw_data_json 제외)
        query = "SELECT * FROM property_master"
        df = pd.read_sql_query(query, conn)
        
        if df.empty:
            print("[WARN] Database is empty. Nothing to export.")
            return

        # 대용량/불필요 컬럼 제외
        cols_to_exclude = ['raw_data_json', 'created_at', 'updated_at']
        df = df.drop(columns=[c for c in cols_to_exclude if c in df.columns])

        # 컬럼 순서 조정 (주요 지표를 앞으로)
        priority_cols = [
            'id', 'canonical_name', 'property_type_std', 
            'district_normalized', 'district', 'cluster_area', 
            'address_road', 'lat', 'lng', 'status_std', 'room_count'
        ]
        existing_priority = [c for c in priority_cols if c in df.columns]
        other_cols = [c for c in df.columns if c not in existing_priority]
        df = df[existing_priority + other_cols]

        # 경로 생성 및 저장
        out_file = Path(export_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 이전 파일이 있다면 삭제 시도 (강제 갱신)
        if out_file.exists():
            out_file.unlink()

        df.to_csv(export_path, index=False, encoding='utf-8-sig')
        
        print(f"\n✨ CSV Export Success!")
        print(f"   - 경로: {export_path}")
        print(f"   - 건수: {len(df)} rows")
        print(f"   - 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   - 실제 포함된 구: {df['district_normalized'].unique() if 'district_normalized' in df.columns else 'N/A'}")

    except Exception as e:
        print(f"[ERROR] CSV 내보내기 중 에러: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    export_full_data()
