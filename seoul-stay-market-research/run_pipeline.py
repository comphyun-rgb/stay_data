import os
import sys
from app.db import init_db
from app.collectors.seoul_open_data import SeoulOpenDataCollector
from app.collectors.visit_seoul import VisitSeoulCollector
from app.pipelines.build_master import process_and_merge_to_master
from scripts.export_data import export_full_data

def run_all():
    print("=== [1/4] DB 초기화 확인 ===")
    init_db()
    
    print("\n=== [2/4] 서울시 인허가 데이터 수집 (상세 정보 포함) ===")
    seoul_collector = SeoulOpenDataCollector()
    seoul_items = seoul_collector.run()
    if seoul_items:
        process_and_merge_to_master(seoul_items, "seoul_open_data")
    else:
        print("서울시 데이터를 수집하지 못했습니다.")
    
    print("\n=== [3/4] Visit Seoul 데이터 수집 ===")
    visit_collector = VisitSeoulCollector()
    visit_items = visit_collector.run()
    if visit_items:
        process_and_merge_to_master(visit_items, "visit_seoul")
    else:
        print("Visit Seoul 데이터를 수집하지 못했습니다.")
        
    print("\n=== [4/4] 결과물 CSV 내보내기 ===")
    export_full_data()
    print("\n작업이 모두 완료되었습니다! data/exports/property_master_full.csv 파일을 확인해 주세요.")

if __name__ == "__main__":
    run_all()
