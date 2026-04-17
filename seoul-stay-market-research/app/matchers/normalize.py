import re

def normalize_name(name: str) -> str:
    """
    고유 명칭에서 노이즈 제거 및 표준화
    """
    if not name:
        return ""
    
    # 소문자 변환
    name = name.lower()
    
    # 특수문자 제거
    name = re.sub(r'[^\w\s가-힣]', '', name)
    
    # 불필요한 공백 제거
    name = " ".join(name.split())
    
    # 숙소 관련 일반 명사 제거 (비교를 위해)
    suffixes = ["호텔", "호스텔", "게스트하우스", "민박", "hotel", "hostel", "guesthouse"]
    for s in suffixes:
        name = name.replace(s, "").strip()
        
    return name

def normalize_address(address: str) -> str:
    """
    주소 표준화 (도로명 주소 위주)
    """
    if not address:
        return ""
    
    # 기본적인 정제
    address = " ".join(address.split())
    
    # '서울특별시' 등 공통 접두사 처리
    address = address.replace("서울특별시 ", "서울 ").replace("서울시 ", "서울 ")
    
    return address
