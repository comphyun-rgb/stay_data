import requests
from ..config import VISIT_SEOUL_API_KEY

BASE_URL = "http://openapi.seoul.go.kr:8088"

# ──────────────────────────────────────────────────────────────────────
# Visit Seoul 숙박 관련 활성 서비스명 (수정 가능 항목)
# 서울 열린데이터 광장에서 서비스명이 변경되면 아래 목록을 수정하세요.
# ──────────────────────────────────────────────────────────────────────
SERVICES = {
    "SebcHotelListKor": {
        "label": "Visit Seoul 호텔 (한국어)",
        "name_col": "NAME_KOR",
        "gu_col": "H_KOR_GU",
        "dong_col": "H_KOR_DONG",
        "type_col": "CATE3_NAME",
        "addr_col": "ADD_KOR_ROAD",
        "lat_col": None,
        "lng_col": None,
    },
    "SebcGuestHouseEng": {
        "label": "Visit Seoul 게스트하우스 (영어)",
        "name_col": "NAME_ENG",
        "gu_col": "H_ENG_GU",
        "dong_col": "H_ENG_DONG",
        "type_col": None,          # 고정값: 게스트하우스
        "addr_col": None,
        "lat_col": None,
        "lng_col": None,
    },
}

# 분석 대상 구 필터 (영문/한문 혼재 → 부분 매칭)
TARGET_GU_KEYWORDS = ["마포", "중구", "종로", "서대문", "Mapo", "Jung", "Jongno", "Seodaemun"]


class VisitSeoulCollector:
    """
    Visit Seoul(서울 열린데이터 광장) 숙박 정보 수집기.

    활성 서비스:
      - SebcHotelListKor : 호텔 목록 (시 전체, 159건)
      - SebcGuestHouseEng: 게스트하우스 영문 목록 (시 전체, 698건)

    ※ 서비스명이 변경되면 모듈 상단 SERVICES 딕셔너리를 수정하세요.
    """

    def __init__(self, api_key: str = VISIT_SEOUL_API_KEY):
        self.api_key = api_key

    # ------------------------------------------------------------------
    def _validate_key(self) -> bool:
        if not self.api_key or self.api_key.strip() in ("", "your_visit_seoul_api_key"):
            print("[ERROR] VISIT_SEOUL_API_KEY 가 설정되지 않았거나 기본값입니다. .env 파일을 확인하세요.")
            return False
        return True

    # ------------------------------------------------------------------
    def _fetch_one(self, service_name: str, meta: dict, end: int = 1000) -> list:
        """단일 서비스 수집 후 공통 구조로 변환"""
        url = f"{BASE_URL}/{self.api_key}/json/{service_name}/1/{end}"
        print(f"[DEBUG] 요청 URL      : {url}")
        print(f"[DEBUG] 서비스명       : {service_name} ({meta['label']})")

        try:
            response = requests.get(url, timeout=15)
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] 네트워크 오류 : {e}")
            return []

        print(f"[DEBUG] 응답 Status  : {response.status_code}")

        if response.status_code != 200:
            print(f"[ERROR] HTTP {response.status_code}")
            print(f"[DEBUG] 응답 body    : {response.text[:500]}")
            return []

        try:
            data = response.json()
        except ValueError:
            print("[ERROR] JSON 파싱 실패 — API가 JSON 이 아닌 형식을 반환했습니다.")
            print(f"[DEBUG] 응답 body    : {response.text[:500]}")
            return []

        if service_name not in data:
            result = data.get("RESULT", {})
            code = result.get("CODE", "")
            msg  = result.get("MESSAGE", "")
            print(f"[ERROR] 응답에 '{service_name}' 키가 없습니다.")
            if code:
                print(f"        API 응답 코드: {code} - {msg}")
            print(f"[DEBUG] 최상위 키: {list(data.keys())}")
            return []

        block = data[service_name]
        result_code = block.get("RESULT", {}).get("CODE", "")
        if result_code and result_code != "INFO-000":
            msg = block.get("RESULT", {}).get("MESSAGE", "")
            print(f"[ERROR] API 오류: {result_code} - {msg}")
            return []

        rows = block.get("row", [])
        total = block.get("list_total_count", "?")
        print(f"[INFO]  수집: {len(rows)}건 / 전체 {total}건")

        # 공통 구조로 변환
        normalized = []
        for row in rows:
            name = row.get(meta["name_col"], "").strip()
            if not name:
                continue

            gu = row.get(meta["gu_col"], "") or ""
            # 분석 대상 구 필터링
            if not any(kw in gu for kw in TARGET_GU_KEYWORDS):
                continue

            prop_type = (row.get(meta["type_col"], "") if meta["type_col"] else "게스트하우스") or "숙박"
            addr = (row.get(meta["addr_col"], "") if meta["addr_col"] else "") or ""
            dong = row.get(meta["dong_col"], "") or ""
            if not addr and gu and dong:
                addr = f"서울특별시 {gu} {dong}"

            normalized.append({
                "_source": service_name,
                "NM": name,
                "ADDR": addr,
                "TYPE": prop_type,
                "LAT": None,
                "LNG": None,
                "_district_name": gu,   # 구 이름 보존 (build_master에서 district 컬럼에 저장)
            })

        print(f"[INFO]  분석 대상 지역 필터 후: {len(normalized)}건")
        return normalized

    # ------------------------------------------------------------------
    def run(self) -> list:
        print("=" * 55)
        print("Visit Seoul 데이터 수집 시작")
        print("=" * 55)

        if not self._validate_key():
            return []

        all_items = []
        for svc, meta in SERVICES.items():
            print()
            items = self._fetch_one(svc, meta)
            all_items.extend(items)

        print(f"\n[TOTAL] 총 {len(all_items)}건 수집 완료")
        return all_items
