import sqlite3
import pandas as pd
from pathlib import Path

def check_duplicates():
    db_path = "data/seoul_stay.db"
    report_path = "data/exports/duplicate_candidates.csv"
    
    if not Path(db_path).exists():
        print("Error: Database not found.")
        return

    conn = sqlite3.connect(db_path)
    
    print("=== 중복 후보 점검 시작 ===")
    
    # 1. 이름 + 주소 중복 (가장 흔한 케이스)
    query_name_addr = """
        SELECT canonical_name, address_road, COUNT(*) as cnt
        FROM property_master
        GROUP BY canonical_name, address_road
        HAVING cnt > 1
    """
    df_name_addr = pd.read_sql_query(query_name_addr, conn)
    print(f"  - 이름+주소 동일 중복: {len(df_name_addr)}개 그룹 발견")

    # 2. 전화번호 중복
    query_phone = """
        SELECT phone, COUNT(*) as cnt
        FROM property_master
        WHERE phone IS NOT NULL AND phone != ''
        GROUP BY phone
        HAVING cnt > 1
    """
    df_phone = pd.read_sql_query(query_phone, conn)
    print(f"  - 전화번호 동일 중복: {len(df_phone)}개 그룹 발견")

    # 3. 좌표 근접성 (약 10~20m 이내)
    # SQLite 특성상 가벼운 소수점 truncation으로 근사 중복 필터링
    query_proximity = """
        SELECT printf('%.4f', lat) as lat_fixed, printf('%.4f', lng) as lng_fixed, COUNT(*) as cnt
        FROM property_master
        WHERE lat IS NOT NULL
        GROUP BY lat_fixed, lng_fixed
        HAVING cnt > 1
    """
    df_prox = pd.read_sql_query(query_proximity, conn)
    print(f"  - 좌표 근접(소수점 4자리 동일) 중복: {len(df_prox)}개 그룹 발견")

    # 리포트 통합 저장
    with pd.ExcelWriter("data/exports/duplication_report.xlsx") if "xlsx" in str(report_path) else open(report_path, "w") as f:
        # 간단히 CSV로 통합 출력 (실제 분석용)
        all_dupes = pd.concat([df_name_addr, df_phone, df_prox], axis=0, sort=False)
        all_dupes.to_csv(report_path, index=False, encoding='utf-8-sig')

    conn.close()
    print(f"\n✅ 중복 점검 리포트가 생성되었습니다: {report_path}")

if __name__ == "__main__":
    check_duplicates()
