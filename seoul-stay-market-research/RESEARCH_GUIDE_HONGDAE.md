# 🚩 홍대권 파일럿 리서치 가이드 (Pilot Research Guide)

본 문서는 홍대권역(Hongdae Cluster)의 숙박 시설을 대상으로 한 OTA(Agoda, Booking.com, Airbnb) 가격 및 평점 조사 가이드라인입니다.

## 1. 리서치 표준 기준 (Standard Criteria)
모든 조사는 비교 가능성을 위해 아래 조건을 엄격히 준수합니다.

| 항목 | 표준값 | 비고 |
| :--- | :--- | :--- |
| **인원 (Guests)** | 2명 | 성인 2인 기준 |
| **숙박일수 (Nights)** | 1박 | 요일별 편차 고려 |
| **체크인 날짜** | 조사일 + 14일 | 예약 가능성 및 가격 안정성 고려 |
| **객실 유형** | 최저가 옵션 | 해당 숙소에서 가장 저렴한 객실 타입 선택 |
| **가격 기준 (KRW)** | 세금/봉사료 포함 총액 | OTA 화면에 표시되는 최종 결제 금액 기준 |

## 2. 조사 대상 추출 및 워크플로우
1. **대상 선정**: `v_hongdae_active_target_sample` 뷰를 통해 추출된 50개 샘플 숙소.
2. **OTA 검색**: Agoda, Booking.com, Airbnb에서 이름/주소로 검색.
3. **매핑 기록**: 숙소를 찾으면 URL과 리스팅 이름을 기록 (`ota_listing_map`).
4. **스냅샷 기록**: 현재 날짜 기준 가격, 평점, 리뷰 수 기록 (`ota_snapshot`).
5. **특이사항**: 화면에 표시되지 않거나 폐업 의심 시 `note` 컬럼에 기록.

## 3. CSV 입력 템플릿 항목 (Pilot Template)
조사자는 다음 순서로 구성된 CSV 파일에 기록합니다.

1. `property_entity_id`: 시스템상의 엔티티 ID (필수)
2. `entity_name`: 시스템상의 숙소 이름 (참조용)
3. `ota_source`: agoda / booking_com / airbnb
4. `raw_listing_name`: OTA에 표시된 숙소 이름
5. `raw_listing_url`: OTA 상세 페이지 고유 링크 (매핑 키)
6. `checkin_date`: 조사 대상 체크인 날짜 (YYYY-MM-DD)
7. `price_total_krw`: 최종 결제 총액
8. `rating`: 현재 평점 (예: 8.5)
9. `review_count`: 리뷰 개수
10. `room_type`: 조사한 객실 이름
11. `refundable_yn`: 환불 가능 여부 (Y/N)
12. `breakfast_yn`: 조식 포함 여부 (Y/N)
13. `availability_status`: 예약 가능 여부 (available / sold_out)

## 4. 매칭 및 검수 규칙
- **Matched**: 이름과 위치가 100% 일치할 때.
- **Review Needed**: 이름이 약간 다르거나(예: 한국어 vs 영어) 위치가 애매할 때.
- **Rejected**: 이름은 같으나 전혀 다른 위치의 숙소일 때.

## 5. 특이사항 처리 (Note Handling)
- 가격이 평소보다 지나치게 비싼 경우(이벤트 등) 사유 기재.
- 해당 일자에 모든 객실이 매진(`sold_out`)인 경우 가격은 0으로 기록하고 상태 표시.
