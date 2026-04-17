import requests
from ..config import SEOUL_OPEN_DATA_API_KEY

BASE_URL = "http://openapi.seoul.go.kr:8088"

TARGET_DISTRICTS = {
    "MP": "마포구",
    "JG": "중구",
    "JN": "종로구",
    "SM": "서대문구",
}

BUSINESS_TYPES = {
    "031101": "관광숙박업",
    "031103": "일반숙박업",
    "031104": "외국인관광도시민박업",
}


class SeoulOpenDataCollector:
    def __init__(self, api_key: str = SEOUL_OPEN_DATA_API_KEY):
        self.api_key = api_key

    def _validate_key(self) -> bool:
        if not self.api_key or self.api_key.strip() == "":
            print("[ERROR] SEOUL_OPEN_DATA_API_KEY 가 설정되지 않았습니다.")
            return False
        return True

    def fetch_by_type_and_district(self, biz_code: str, district_code: str, end: int = 1000) -> list:
        # [Fix] 수집 안정성을 위해 1000건 단위로 강제 제한
        service_name = f"LOCALDATA_{biz_code}_{district_code}"
        url = f"{BASE_URL}/{self.api_key}/json/{service_name}/1/{end}"

        try:
            response = requests.get(url, timeout=15)
            if response.status_code != 200:
                print(f"  [WARN] {service_name} — HTTP {response.status_code}")
                return []

            # JSON 파싱 전 응답 내용 검증
            try:
                data = response.json()
            except Exception:
                print(f"  [ERROR] {service_name} — JSON 파싱 실패 (응답 내용: {response.text[:100]}...)")
                return []

            if service_name not in data:
                result = data.get("RESULT", {})
                code = result.get("CODE", "")
                if code == "INFO-200":
                    return []
                print(f"  [WARN] {service_name} — 응답 키 없음 ({code})")
                return []

            block = data[service_name]
            rows = block.get("row", [])
            print(f"  ✅ {service_name} — {len(rows)}건 수집 완료")

            for row in rows:
                row["_district_name_raw"] = TARGET_DISTRICTS[district_code]
                row["_biz_type_label"] = BUSINESS_TYPES[biz_code]
            return rows

        except Exception as e:
            print(f"  [ERROR] {service_name} 수집 중 예외 발생 : {e}")
            return []

    def run(self) -> list:
        if not self._validate_key():
            return []

        all_items = []
        for biz_code, biz_label in BUSINESS_TYPES.items():
            print(f"\n[{biz_label}] 수집 중...")
            for dist_code in TARGET_DISTRICTS:
                # 안전하게 1000건씩 수집
                items = self.fetch_by_type_and_district(biz_code, dist_code, end=1000)
                all_items.extend(items)

        return all_items
