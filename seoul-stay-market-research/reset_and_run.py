import os
import sys
from app.db import init_db
from app.collectors.seoul_open_data import SeoulOpenDataCollector
from app.collectors.visit_seoul import VisitSeoulCollector
from app.pipelines.build_master import process_and_merge_to_master
from scripts.export_data import export_full_data
from scripts.create_views import create_views
from scripts.check_duplicates import check_duplicates
from scripts.check_mismatches import check_district_mismatch
from scripts.build_entity_layer import build_entity_layer

def full_pipeline_master():
    """수집-정제-엔티티구축-분석레이어 통합 실행"""
    db_path = "data/seoul_stay.db"
    
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"\n[0] 새로운 엔티티 레이어 구축을 위해 DB를 초기화했습니다.")
        except Exception as e:
            print(f"DB 초기화 에러: {e}")
    
    print("\n=== [1/6] DB 스키마 생성 및 초기화 ===")
    init_db()
    
    print("\n=== [2/6] 서울시 인허가 데이터 수집 (Seodaemun Code Fixed) ===")
    seoul_collector = SeoulOpenDataCollector()
    seoul_items = seoul_collector.run()
    if seoul_items:
        process_and_merge_to_master(seoul_items, "seoul_open_data")
    
    print("\n=== [3/6] Visit Seoul 데이터 보강 (Enrichment Only) ===")
    visit_collector = VisitSeoulCollector()
    visit_items = visit_collector.run()
    if visit_items:
        process_and_merge_to_master(visit_items, "visit_seoul")
        
    print("\n=== [4/6] 엔티티 레이어 구축 (Deduplication) ===")
    build_entity_layer()  # 이름/주소 기반 물리적 숙소 통합
        
    print("\n=== [5/6] 분석 레이어(Views) 및 리포트 생성 ===")
    create_views()              # 엔티티 기반 Target Views 생성
    check_district_mismatch()   # 정합성 점검
    check_duplicates()          # 중복 후보 점검 (마스터 기준)
    
    print("\n=== [6/6] 최종 데이터 내보내기 ===")
    export_full_data()
    
    print("\n" + "="*50)
    print("🚀 OTA 리서치 준비 완료! (엔티티 레이어 구축 성공)")
    print("1. 조사 타깃: v_research_target (엔티티 기준 리스트)")
    print("2. 권역별 타깃: v_hongdae_active_target 등")
    print("="*50)

if __name__ == "__main__":
    full_pipeline_master()
