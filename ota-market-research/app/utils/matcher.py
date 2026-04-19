import re

def normalize_name(name):
    if not name: return ""
    # Remove Korean parenthesis content like (주), (사)
    name = re.sub(r'\([가-힣]+\)', '', name)
    name = name.lower()
    noise = [
        "hotel", "hostel", "guesthouse", "stay", "house", "inn", "apart", "apartment",
        "hongdae", "seoul", "shinchon", "yeonnam", "hapjeong", "sangsu",
        "게스트하우스", "호스텔", "호텔", "스테이", "민박", "홍대", "서울", "신촌", "연남", "합정",
        "by", "collection", "autograph", "ltd", "co"
    ]
    for n in noise:
        name = name.replace(n, "")
    # Remove everything except alphanumeric and Korean
    name = re.sub(r'[^a-zA-Z0-9가-힣]', '', name)
    return name.strip()

def normalize_address(addr):
    if not addr: return {"dong": "", "street": ""}
    # 1. Clean address string
    addr = str(addr).replace(",", " ").replace("(", " ").replace(")", " ")
    
    # 2. Extract Dong
    dong_match = re.search(r'([가-힣]+동)', addr)
    dong = dong_match.group(1) if dong_match else ""
    
    # 3. Extract Street (Korean) - e.g. 양화로 141
    street_match = re.search(r'([가-힣]+로\s*\d+)', addr)
    street = street_match.group(1) if street_match else ""
    
    # 4. Extract Street (English) - e.g. Yanghwa-ro 130 or 130 Yanghwa-ro
    if not street:
        en_match = re.search(r'(\d+)\s*([A-Za-z\-]+ro)', addr)
        if en_match:
            street = en_match.group(2) + en_match.group(1)
        else:
            en_match2 = re.search(r'([A-Za-z\-]+ro)\s*(\d+)', addr)
            if en_match2:
                street = en_match2.group(1) + en_match2.group(2)

    return {
        "dong": dong,
        "street": re.sub(r'[^a-zA-Z0-9가-힣]', '', street).lower()
    }

def calculate_name_similarity(name1, name2):
    n1 = normalize_name(name1)
    n2 = normalize_name(name2)
    if not n1 or not n2: return 0.0
    if n1 == n2: return 1.0
    if n1 in n2 or n2 in n1: return 0.9 # High score for containment
    
    overlap = len(set(n1) & set(n2))
    score = overlap / max(len(n1), len(n2))
    return score

def get_similarity_level(score):
    if score >= 0.9: return "exact"
    if score >= 0.6: return "high"
    if score >= 0.3: return "medium"
    return "mismatch"
