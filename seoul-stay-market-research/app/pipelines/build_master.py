import json
import math
from pathlib import Path
from ..db import SessionLocal
from ..models.property_master import PropertyMaster
from ..models.property_alias import PropertyAlias
from ..matchers.score_match import calculate_match_score, determine_status

try:
    from pyproj import Transformer
    _transformer = Transformer.from_crs("EPSG:2097", "EPSG:4326", always_xy=True)
    HAS_PYPROJ = True
except ImportError:
    HAS_PYPROJ = False

# [Anchor] 홍대입구역 중심점
HONGDAE_ANCHOR = (37.5575, 126.9245)

def calculate_distance(lat1, lon1, lat2, lon2):
    """Haversine 공식으로 두 좌표 간 거리(m) 계산"""
    if None in [lat1, lon1, lat2, lon2]: return float('inf')
    R = 6371000 # 지구 반지름(m)
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def get_hongdae_zone_refined(lat, lng, address):
    """좌표 기반 홍대 상권 존(Zone) 판정 및 키워드 보정"""
    dist = calculate_distance(lat, lng, HONGDAE_ANCHOR[0], HONGDAE_ANCHOR[1])
    addr = (address or "").replace(" ", "")
    
    zone = ""
    # 1차: 거리 기반 분류
    if dist <= 500:
        zone = "core_hongdae"
    elif dist <= 900:
        zone = "hongdae_area"
    elif dist <= 1200:
        zone = "fringe_hongdae"
    
    # 2차: 키워드 보정 (거리 경계에 있더라도 특정 동네면 포함 가능성 고려)
    if not zone and any(k in addr for k in ["서교", "동교", "연남", "합정"]):
        if dist <= 1500: # 키워드가 있다면 반경을 1.5km까지 Fringe로 확장 인정
            zone = "fringe_hongdae"
            
    return zone

def tm_to_wgs84(x_tm, y_tm):
    if not HAS_PYPROJ or not x_tm or not y_tm:
        return None, None, "NoTransform"
    try:
        x_f, y_f = float(x_tm), float(y_tm)
        if x_f == 0 or y_f == 0: return None, None, "ZeroValue"
        lng, lat = _transformer.transform(x_f, y_f)
        if 37.0 <= lat <= 38.0 and 126.0 <= lng <= 128.0:
            return round(lat, 6), round(lng, 6), "Success"
        return None, None, "OutOfRange"
    except:
        return None, None, "Error"

def extract_district_from_address(address: str) -> str:
    if not address: return ""
    parts = address.split()
    for p in parts:
        if p.endswith("구"): return p
    return ""

def classify_property_type(raw_type: str) -> str:
    if not raw_type: return "unknown"
    t = raw_type.replace(" ", "")
    if any(k in t for k in ["관광호텔", "가족호텔", "소형호텔", "의료관광호텔", "특1급", "특2급", "1급", "2급"]): return "hotel"
    if "호스텔" in t: return "hostel"
    if any(k in t for k in ["게스트하우스", "외국인관광도시민박", "도시민박", "한옥"]): return "guesthouse"
    if "일반숙박업" in t: return "motel_or_lodging"
    if any(k in t for k in ["생활숙박", "레지던스"]): return "residence"
    return "unknown"

def classify_status(raw_status: str, detail_status: str) -> str:
    s = f"{raw_status or ''} {detail_status or ''}".strip()
    if not s: return "unknown"
    if any(k in s for k in ["영업/정상", "영업중", "정상"]): return "active"
    if any(k in s for k in ["폐업", "휴업", "취소", "중단", "말소"]): return "closed"
    return "unknown"

def get_cluster_area(district: str, address: str, lat: float = None, lng: float = None) -> str:
    # 1순위: 좌표 기반 홍대권 판정
    h_zone = get_hongdae_zone_refined(lat, lng, address)
    if h_zone: return "홍대권"
    
    if not address or not district: return ""
    addr = address.replace(" ", "")
    # 2순위: 기타 권역 키워드 기반 판정
    if "마포구" in district and any(k in addr for k in ["창천", "노고산", "대흥"]): return "신촌권"
    if "서대문구" in district and any(k in addr for k in ["대창", "신촌"]): return "신촌권"
    if "중구" in district and any(k in addr for k in ["명동", "을지로", "충무로", "남대문", "회현"]): return "명동권"
    if "종로구" in district and any(k in addr for k in ["익선", "안국", "삼청", "인사", "종로"]): return "종로권"
    return ""

def _extract_seoul_data(item: dict) -> dict:
    raw_x = item.get("X") or item.get("x")
    raw_y = item.get("Y") or item.get("y")
    lat, lng, coord_res = tm_to_wgs84(raw_x, raw_y)

    address = (item.get("RDNWHLADDR") or item.get("SITEWHLADDR") or "").strip()
    dist_raw = item.get("_district_name_raw", "")
    dist_norm = extract_district_from_address(address) or dist_raw

    raw_type = (item.get("TRSTLODGCLNM") or item.get("CULPHYEDCOBNM") or item.get("_biz_type_label") or "").strip()
    
    h_zone = get_hongdae_zone_refined(lat, lng, address)

    return {
        "name": item.get("BPLCNM", "").strip(),
        "address": address,
        "lat": lat, "lng": lng, "raw_x": raw_x, "raw_y": raw_y, "coord_result": coord_res,
        "district": dist_raw,
        "district_normalized": dist_norm,
        "cluster_area": get_cluster_area(dist_norm, address, lat, lng),
        "hongdae_zone": h_zone,
        "property_type_raw": raw_type,
        "property_type_std": classify_property_type(raw_type),
        "raw_status": item.get("TRDSTATENM", "").strip(),
        "raw_status_detail": item.get("DTLSTATENM", "").strip(),
        "status_std": classify_status(item.get("TRDSTATENM"), item.get("DTLSTATENM")),
        "name_eng": item.get("ENGSTNTRNMNM", "").strip(),
        "phone": item.get("SITETEL", "").strip(),
        "floors_above": int(item["JISGNUMLAY"]) if item.get("JISGNUMLAY") and str(item["JISGNUMLAY"]).isdigit() else None,
        "floors_below": int(item["UNDERNUMLAY"]) if item.get("UNDERNUMLAY") and str(item["UNDERNUMLAY"]).isdigit() else None,
        "room_count": int(item["STROOMCNT"]) if item.get("STROOMCNT") and str(item["STROOMCNT"]).isdigit() else None,
        "building_area": float(item["FACILAR"]) if item.get("FACILAR") and float(item["FACILAR"]) > 0 else None,
        "license_date": item.get("APVPERMYMD", "").strip(),
        "raw_json": json.dumps(item, ensure_ascii=False)
    }

def _extract_visit_seoul_data(item: dict) -> dict:
    address = (item.get("ADDR") or "").strip()
    dist_raw = item.get("_district_name", "")
    dist_norm = extract_district_from_address(address) or dist_raw
    lat, lng = item.get("LAT"), item.get("LNG")
    h_zone = get_hongdae_zone_refined(lat, lng, address)
    
    return {
        "name": (item.get("NM") or "").strip(),
        "address": address,
        "lat": lat, "lng": lng,
        "district": dist_raw,
        "district_normalized": dist_norm,
        "cluster_area": get_cluster_area(dist_norm, address, lat, lng),
        "hongdae_zone": h_zone,
        "property_type_raw": (item.get("TYPE") or "").strip(),
        "property_type_std": classify_property_type((item.get("TYPE") or "").strip()),
        "status_std": "active",
    }

def process_and_merge_to_master(source_items: list, source_name: str):
    if not source_items: return
    db = SessionLocal()
    try:
        matched = created = 0
        for item in source_items:
            target = _extract_seoul_data(item) if source_name == "seoul_open_data" else _extract_visit_seoul_data(item)
            name = target["name"]
            if not name: continue

            masters = db.query(PropertyMaster).all()
            best_score = 0; best_match = None
            for m in masters:
                candidate = {"name": m.canonical_name, "address": m.address_road, "lat": m.lat, "lng": m.lng, "type": m.property_type_raw}
                score, _ = calculate_match_score(target, candidate)
                if score > best_score: best_score, best_match = score, m

            conf_status = determine_status(best_score)

            if conf_status == "confirmed" and best_match:
                if not best_match.lat: best_match.lat = target.get("lat")
                if not best_match.lng: best_match.lng = target.get("lng")
                if not best_match.cluster_area: best_match.cluster_area = target.get("cluster_area")
                if not best_match.hongdae_zone: best_match.hongdae_zone = target.get("hongdae_zone")
                alias = PropertyAlias(property_id=best_match.id, source_name=source_name, alias_name=name, alias_address=target["address"], match_confidence=best_score, is_verified=True)
                db.add(alias); matched += 1
            else:
                if source_name == "visit_seoul": continue
                new_master = PropertyMaster(
                    canonical_name=name, property_type_std=target["property_type_std"],
                    district_normalized=target["district_normalized"], cluster_area=target["cluster_area"],
                    hongdae_zone=target["hongdae_zone"], address_road=target["address"],
                    lat=target["lat"], lng=target["lng"], status_std=target["status_std"],
                    phone=target.get("phone"), room_count=target.get("room_count"),
                    license_date=target.get("license_date"), property_type_raw=target["property_type_raw"],
                    raw_status=target.get("raw_status"), raw_status_detail=target.get("raw_status_detail"),
                    district=target["district"], raw_x=str(target["raw_x"]) if target["raw_x"] else None,
                    raw_y=str(target["raw_y"]) if target["raw_y"] else None,
                    raw_data_json=target.get("raw_json"), source_priority=source_name,
                    name_eng=target.get("name_eng"), floors_above=target.get("floors_above"),
                    floors_below=target.get("floors_below"), building_area=target.get("building_area")
                )
                db.add(new_master); created += 1
        db.commit()
    except Exception as e:
        print(f"[{source_name}] Error: {e}"); db.rollback()
    finally:
        db.close()
