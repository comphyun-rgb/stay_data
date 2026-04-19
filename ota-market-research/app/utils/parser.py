import re
from typing import Tuple, Optional

class OTAParser:
    """
    OTA 원문 데이터를 표준화된 포맷으로 변환하는 파서 유틸리티.
    """
    
    @staticmethod
    def classify_analysis_unit(name: str, max_guests: int) -> str:
        """
        대표 분석 단위 분류:
        - dorm_1p: 도미토리 1인
        - double_2p: 일반실 2인 (더블/트윈)
        - family_4p: 3-4인 다인실
        """
        name = name.lower()
        if any(kw in name for kw in ['dorm', 'bunk', 'bed in', '객실 내 침대']):
            return 'dorm_1p'
        if max_guests >= 3:
            return 'family_4p'
        if max_guests == 2:
            return 'double_2p'
        if max_guests == 1:
            return 'single_1p'
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
