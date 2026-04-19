import re
from typing import Tuple, Optional

class OTAParser:
    """
    OTA 원문 데이터를 표준화된 포맷으로 변환하는 파서 유틸리티.
    """
    
    @staticmethod
    def classify_analysis_unit(name: str, max_guests: int) -> str:
        """
        비교용 대분류 (room_analysis_type):
        - dorm_1p: 도미토리 침대
        - double_2p: 2인실 (더블/트윈)
        - family_4p: 3-4인실
        """
        name = name.lower()
        if any(kw in name for kw in ['dorm', 'bunk', 'bed in', '객실 내 침대']):
            return 'dorm_1p'
        if max_guests >= 3:
            return 'family_4p'
        if max_guests == 2:
            return 'double_2p'
        return 'other'

    @staticmethod
    def parse_room_type(name: str) -> str:
        name = name.lower()
        if any(kw in name for kw in ['dorm', 'bunk', 'bed in']):
            return 'dorm_bed'
        if any(kw in name for kw in ['suite', 'penthouse']):
            return 'suite'
        if any(kw in name for kw in ['family', 'quad', 'triple']):
            return 'family_room'
        if any(kw in name for kw in ['studio', 'loft', 'entire']):
            return 'studio'
        if any(kw in name for kw in ['hotel', 'deluxe', 'superior', 'standard', 'twin', 'double']):
            return 'hotel_room'
        if any(kw in name for kw in ['private', 'single', 'double']):
            return 'private_room'
        return 'unknown'

    @staticmethod
    def parse_bathroom_type(raw_text: str) -> Tuple[str, str]:
        """
        (private_bathroom_yn, bathroom_type) 반환
        """
        text = raw_text.lower()
        if any(kw in text for kw in ['private', '전용', '개별']):
            return 'Y', 'private'
        if any(kw in text for kw in ['shared', '공용', '공동']):
            return 'N', 'shared'
        return 'Y', 'unknown' # 기본값은 전용으로 가정하되 타입은 불명

    @staticmethod
    def parse_max_guests(text: str) -> int:
        # 'Max 2 adults', '2인 기준', 'Sleeps 4' 등 패턴 매칭
        match = re.search(r'(\d+)', text)
        if match:
            return int(match.group(1))
        return 2 # 기본값

    @staticmethod
    def parse_refundable(text: str) -> str:
        text = text.lower()
        if any(kw in text for kw in ['free cancellation', '무료 취소', 'refundable']):
            return 'Y'
        if any(kw in text for kw in ['non-refundable', '취소 불가']):
            return 'N'
        return 'NA'

    @staticmethod
    def parse_tax_included(text: str) -> str:
        text = text.lower()
        if any(kw in text for kw in ['tax included', '세금 포함', 'final price']):
            return 'Y'
        if any(kw in text for kw in ['tax not included', '세금 별도']):
            return 'N'
        return 'Y' # 한국 OTA는 대체로 포함가가 기본

    @staticmethod
    def parse_facilities(text: str) -> dict:
        """
        시설 텍스트에서 주요 항목 추출
        """
        text = text.lower()
        return {
            "elevator_yn": "Y" if any(kw in text for kw in ['elevator', 'lift', '엘리베이터']) else "N",
            "parking_yn": "Y" if any(kw in text for kw in ['parking', '주차']) else "N",
            "breakfast_yn": "Y" if any(kw in text for kw in ['breakfast', '조식']) else "N",
            "wifi_yn": "Y" if any(kw in text for kw in ['wifi', 'internet', '와이파이']) else "Y", # 기본 제공 가정
            "kitchen_yn": "Y" if any(kw in text for kw in ['kitchen', '주방']) else "N",
            "laundry_yn": "Y" if any(kw in text for kw in ['laundry', 'washing', '세탁']) else "N",
            "aircon_yn": "Y" if any(kw in text for kw in ['air con', 'cooling', '에어컨']) else "Y"
        }

    @staticmethod
    def parse_availability(text: str) -> dict:
        """
        판매 상태 텍스트에서 상태 코드 추출
        """
        text = text.lower()
        is_sold_out = any(kw in text for kw in ['sold out', '예약 마감', '불가능', 'no longer available'])
        return {
            "sold_out_yn": is_sold_out,
            "bookable_yn": not is_sold_out,
            "observed_price_yn": not is_sold_out,
            "availability_text": text
        }
