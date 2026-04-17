# Seoul Stay Market Research (서울 숙박 시장 조사 시스템)

본 프로젝트는 서울 내 주요 상권의 데이터를 수집/정합하고, 홍대권역을 대상으로 파일럿 시장 조사(OTA 가격/평점 매핑)를 수행하는 시스템입니다.

## 🚀 현 단계: 홍대 파일럿 (Phase 2 - Pilot)

현재 시스템은 **홍대권역(Hongdae Cluster)**을 대상으로 수동 조사 및 데이터 적재 프로세스를 검증하는 단계입니다.

### 📋 파일럿 운영 흐름 (Workflow)
1. **타깃 추출**: `python3 scripts/export_hongdae_pilot_list.py` 실행 ➔ 조사 대상 CSV 생성.
2. **수동 조사**: `RESEARCH_GUIDE_HONGDAE.md` 기준에 따라 Agoda/Booking.com 검색 및 입력.
3. **데이터 임포트**: `python3 scripts/import_ota_pilot_data.py` 실행 ➔ 매핑 및 가격 스냅샷 적재.
4. **검수**: DB의 `v_hongdae_mapping_status` 뷰를 통해 수집률 및 품질 확인.

## 📂 데이터 레이어 구조

### 1. RAW/CURATED (공급 데이터)
- `property_master`: 공공기관 원본 수집 데이터.
- `property_entity`: 이름/주소 기반 통합된 물리적 숙소 단위.

### 2. MAPPING/SNAPSHOT (시장 데이터)
- `ota_listing_map`: 엔티티와 실제 OTA 상품 페이지 연결 정보.
- `ota_snapshot`: 매핑된 상품의 시점별 가격, 평점, 리뷰 수 스냅샷.

## 📊 리서치 가이드 및 리포트
- [조사 표준 지침 (RESEARCH_GUIDE_HONGDAE.md)](./RESEARCH_GUIDE_HONGDAE.md)
- **주요 뷰**:
  - `v_hongdae_active_target`: 홍대권 영업 중인 숙소 목록.
  - `v_hongdae_mapping_status`: 홍대 권역 리서치 진행 현황 트래킹.
  - `v_hongdae_snapshot_recent`: 홍대 권역 최신 수집 가격 모니터링.

## 📝 향후 과제 (Roadmap)
- [ ] **파일럿 검수**: 홍대권 50건 데이터 적재 후 시스템 정합성 최종 점검.
- [ ] **자동화 확장**: 수동 입력 구조를 자동 크롤링/스크래핑 엔진으로 점진적 전환.
- [ ] **권역 확장**: 홍대 파일럿 성공 후 명동, 종로, 신촌권으로 조사 범위 확대.
