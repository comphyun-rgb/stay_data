# 📊 OTA 데이터 보강 및 수집 전략 가이드 (Phase 5)

본 문서는 Track B의 데이터 충전율을 넘어, 좌표/정책/Snapshot 데이터를 보강하여 실제 시장 가격 지수를 산출하기 위한 전략을 정의합니다.

## 1. 🚀 현 단계: 데이터 보강 및 대표 가격 산출 (Phase 5)
객실/상품 단위의 구조 검증을 완료하고, 이제 **좌표/정책/Snapshot 데이터를 집중적으로 보강**하여 실제 시장 가격 지수를 산출하는 단계입니다.

## 2. OTA별 수집 가능 필드 매트릭스 (Field Matrix)

| 구분 | 필드명 | Agoda | Booking.com | Airbnb | 비고 |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **숙소** | `star_rating` | ○ | ○ | △ | Airbnb는 평점 위주 |
| | `property_type_std` | ◎ | ◎ | ◎ | 필수 표준화 대상 |
| | `raw_lat / lng` | ○ | ○ | ○ | 수집 경로 최적화 필요 |
| **객실** | `room_type_name` | ◎ | ◎ | ○ | |
| | `room_type_std` | ○ | ○ | △ | 텍스트 파싱 필요 |
| | `max_guests` | ◎ | ◎ | ◎ | |
| | `bed_count / type` | ○ | ○ | ○ | |
| **정책** | `private_bathroom_yn` | ○ | ○ | ◎ | Airbnb는 중요 속성 |
| | `cancel_policy_raw` | ○ | ◎ | ◎ | |
| | `tax_included_yn` | △ | ○ | ○ | 지역별 설정 확인 필요 |

- ◎: 매우 안정적 | ○: 수집 가능 | △: 부분 누락 또는 가공 필요

## 2. 좌표 수집 보강 (Coordinate Strategy)

현재 좌표 보유율을 높이기 위한 채널별 확보 경로:
- **Agoda**: 검색 결과 JSON API 또는 상세 페이지의 `hotel_location` 스크립트 객체.
- **Booking.com**: 상세 페이지 내 정적 지도 이미지 URL 파싱 또는 `booking_data` 객체.
- **Airbnb**: 지도 검색(`map_search`) API 응답 또는 상세 페이지 메타데이터.

**우선순위 과제**:
1. 서울시 마스터(Track A) 데이터와 1:1 매칭을 위해 모든 수집기에 `raw_lat`, `raw_lng` 수집 로직을 필수 항목으로 추가.
2. 좌표가 없는 기존 데이터는 상세 페이지 URL 재방문을 통한 보강 작업 수행.

### 📍 좌표 신뢰성 검증 원칙 (Coordinate Verification Principle)
OTA에서 제공하는 좌표는 숙소의 정확한 위치가 아닌, 권역 대표 좌표(Mock/Sample)일 가능성이 있습니다. 따라서 다음 원칙을 준수합니다.
- **수집된 좌표를 그대로 신뢰하지 않는다.**
- 모든 좌표는 실제 숙박업소 POI와의 거리를 측정하여 **Existence Validation** 단계를 거친다.
- 반경 200m 이내에 숙박업소가 확인되지 않는 좌표는 'invalid_suspected'로 분류하여 분석에서 제외하거나 수동 검토한다.

## 3. 표준화 품질 관리 (Standardization)

- **Unknown 관리**: `v_ota_standardization_dist` 뷰를 통해 `unknown`으로 분류된 텍스트를 주기적으로 모니터링하고, 파싱 사전에 반영.
- **Bathroom**: 게스트하우스/호실 분석을 위해 `shared` 타입 오분류 방지 로직 강화.

## 5. 대표 비교 상품 산출 기준 (Representative Price)

데이터 보강 후 SQL을 통해 산출할 대표 가격 기준입니다.

| 상품 유형 | 기준 인원 | 필터 조건 | 대표값 선정 |
| :--- | :---: | :--- | :--- |
| **Hotel / Private** | 2인 | `private_bathroom_yn = 'Y'` | 최저가 상품 |
| **Dormitory** | 1인 | `room_type_std = 'dorm_bed'` | 최저가 상품 |
| **Family Room** | 3~4인 | `max_guests >= 3` | 최저가 상품 |

## 6. 향후 계획 (Next Steps)
- **공간 분석**: 보강된 좌표 데이터를 활용하여 홍대권 권역별(연남, 서교, 합정) 가격 편차 분석.
- **Snapshot 시계열 분석**: 누적된 데이터를 바탕으로 체크인 D-day별 가격 변동성 추적.
- **Track A 매칭**: 좌표 기반 자동 매칭 엔진 가동.
