import sys
import os

# Add the root directory to sys.path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.validate_ota_coordinates import run_actual_validation

def main():
    print("Executing Real Data Verification...")
    results = run_actual_validation(limit=20)
    
    if not results:
        print("No results to report.")
        return

    stats = {
        "confirmed_exact": 0,
        "confirmed_nearby": 0,
        "probable_match": 0,
        "review_needed": 0,
        "invalid_suspected": 0
    }

    print("\n### C. 실제 검증 실행 결과 표 (Actual Verification Results)")
    header = "| ota_source | raw_listing_name | raw_lat | raw_lng | nearest_known_lodging_name | distance_m | name_match | existence_status | note |"
    sep = "|---|---|---|---|---|---|---|---|---|"
    print(header)
    print(sep)

    for r in results:
        dist = round(r["nearest_lodging_distance_m"], 1)
        row = f"| {r['ota_source']} | {r['raw_listing_name']} | {r['raw_lat']:.6f} | {r['raw_lng']:.6f} | {r['nearest_lodging_name']} | {dist} | {r['name_match_status']} | {r['existence_validation_status']} | {r['existence_validation_note']} |"
        print(row)
        stats[r["existence_validation_status"]] += 1

    print("\n### D. 통계 (Statistics)")
    print(f"- confirmed_exact 건수: {stats['confirmed_exact']}")
    print(f"- confirmed_nearby 건수: {stats['confirmed_nearby']}")
    print(f"- review_needed / invalid_suspected 건수: {stats['review_needed'] + stats['invalid_suspected']}")
    
    print("\n### F. 현재 검증 신뢰도와 한계")
    print("- **신뢰도**: Track A 서울시 숙박업 마스터(인허가 데이터 기반)와 직접 비교하므로 좌표 정합성 판정의 객관성 확보.")
    print("- **한계 1**: 마스터 데이터에 누락된 신규 소규모 게스트하우스는 'invalid_suspected'로 오판될 가능성 있음.")
    print("- **한계 2**: 주소 텍스트 기반 정밀 대조 로직은 아직 미완성 (좌표+명칭 위주 판정).")

if __name__ == "__main__":
    main()
