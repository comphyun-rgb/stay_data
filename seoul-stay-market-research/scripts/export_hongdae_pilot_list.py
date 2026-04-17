import sqlite3
import pandas as pd
from pathlib import Path

def export_hongdae_pilot_list():
    db_path = "data/seoul_stay.db"
    export_path = "data/exports/hongdae_pilot_research_list.csv"
    
    if not Path(db_path).exists():
        print("Error: Database not found.")
        return

    conn = sqlite3.connect(db_path)
    
    print("=== 홍대권 파일럿 리서치 타깃 추출 시작 ===")
    
    # 홍대권 active target 중 샘플 50건 추출 로직
    # 우선순위: 좌표 보유 + 다양한 유형 (호텔, 호스텔 등)
    query = """
        SELECT 
            entity_id as property_entity_id,
            display_name as entity_name,
            representative_address,
            district,
            cluster_area,
            lat,
            lng,
            master_count
        FROM v_hongdae_active_target
        ORDER BY master_count DESC, entity_id ASC
        LIMIT 50
    """
    
    df = pd.read_sql_query(query, conn)
    
    if df.empty:
        print("⚠️ 홍대권 조사 대상 데이터가 없습니다.")
        return

    # 조사자가 입력할 빈 컬럼들 추가 (템플릿 기능)
    research_cols = [
        'ota_source', 'raw_listing_name', 'raw_listing_url', 
        'checkin_date', 'price_total_krw', 'rating', 'review_count',
        'room_type', 'refundable_yn', 'breakfast_yn', 'availability_status', 'note'
    ]
    for col in research_cols:
        df[col] = "" # 비어있는 입력 칸 생성

    out_file = Path(export_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    
    df.to_csv(export_path, index=False, encoding='utf-8-sig')
    
    print(f"✅ 홍대권 파일럿 리스트(50개 샘플) 생성 완료: {export_path}")
    print(f"👉 이 파일을 열어 OTA 조사 내용을 입력한 후 다시 업로드하세요.")
    
    conn.close()

if __name__ == "__main__":
    export_hongdae_pilot_list()
