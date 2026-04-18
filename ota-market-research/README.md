# 🏨 OTA Market Research (Track B)

본 프로젝트는 주요 OTA의 시장 리스팅 데이터를 수집, 적재, 분석하는 **Track B 전용 시스템**입니다.

## 🚀 현 단계: 데이터 보강 및 대표 가격 산출 (Phase 5)
객실/상품 단위의 구조 검증을 완료하고, 이제 **좌표/정책/Snapshot 데이터를 집중적으로 보강**하여 실제 시장 가격 지수를 산출하는 단계입니다.

### 📋 주요 업데이트 사항
- **다채널 수집 체계**: 
  - **Agoda**: 브라우저 기반 실시간 25~30건 리스팅 벌크 적재 완료.
  - **Booking.com**: 지역 검색 결과 기반 수집기 구조 마련 및 파일럿 샘플 적재.
  - **Airbnb**: 수동/반수동 샘플 로더를 통한 홍대권 전략 숙소 적재.
- **데이터 보강 엔진**: 
  - `app/utils/parser.py`: 객실 타입, 욕실 여부, 정책 텍스트 표준화 파서 도입.
  - 좌표(`raw_lat/lng`) 및 정책(`refundable_yn`) 수집 로직 강화.
- **Snapshot 반복 적재**: 동일 상품 기준 시계열 가격 데이터 누적 구조 확립.
- **운영용 점검 도구**:
  - `scripts/run_audit.py`: 전체 데이터 적재 현황 및 품질 감사.
  - `scripts/generate_qc_report.py`: 품질 점검(QC) 뷰 리포트 생성.

## 📐 운영 및 점검 방법
```bash
# 데이터 품질 및 적재 현황 점검
python scripts/run_audit.py

# 상세 QC 리포트 출력
python scripts/generate_qc_report.py
```
- **인원**: 성인 2명
- **박수**: 1박
- **체크인 날짜**: 수집일 + 14일 (D+14)
- **우선순위**: Agoda 리스트 하베스팅 ➔ Booking 확장 ➔ Airbnb 특이 숙소 보완

## 📂 운영 명령어
```bash
# 전체 파이프라인 초기화 및 실데이터 파일럿 실행
export PYTHONPATH=$PYTHONPATH:. && python3 reset_and_run.py
```

---
*향후 계획: Track A(서울시 마스터) 엔티티와의 자동 매칭 엔진 개발 및 홍대권 가격 히트맵 분석.*
