from geopy.distance import geodesic

def calculate_distance(lat1, lng1, lat2, lng2):
    """
    두 좌표 사이의 거리 계산 (단위: 미터)
    """
    if None in [lat1, lng1, lat2, lng2]:
        return float('inf')
    
    try:
        dist = geodesic((lat1, lng1), (lat2, lng2)).meters
        return dist
    except Exception:
        return float('inf')

def get_geo_score(dist_meters):
    """
    거리에 따른 점수 부여
    - 20m 이내: 50점
    - 50m 이내: 30점
    """
    if dist_meters <= 20:
        return 50
    elif dist_meters <= 50:
        return 30
    return 0
