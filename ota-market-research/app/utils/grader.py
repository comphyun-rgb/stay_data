import math

def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    # Radius of the Earth in km
    R = 6371.0
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c * 1000 # Convert to meters
    return distance

def calculate_location_score(lat, lng, target_lat=37.556, target_lng=126.923):
    """
    Max 25 points based on distance to center (Hongdae Stn)
    """
    if not lat or not lng: return 5 # Default for unknown
    
    dist_m = calculate_haversine_distance(lat, lng, target_lat, target_lng)
    
    if dist_m < 300: return 25
    if dist_m < 700: return 20
    if dist_m < 1200: return 12
    return 5

def calculate_review_score_component(score_std, count):
    """
    Max 25 points
    - Weight by score and count stability
    """
    base_score = (score_std / 10.0) * 20
    # Stability bonus based on count
    if count >= 1000: stability = 5
    elif count >= 500: stability = 4
    elif count >= 100: stability = 2
    else: stability = 0
    
    return min(25, base_score + stability)

def calculate_facility_score(props):
    """
    Max 30 points
    Simplified mapping for Phase 1
    """
    score = 0
    if props.get('private_bathroom_yn') == 'Y': score += 10
    if props.get('elevator_yn') == 'Y': score += 5
    if props.get('breakfast_yn') == 'Y': score += 5
    if props.get('wifi_yn') == 'Y': score += 3
    if props.get('aircon_yn') == 'Y': score += 3
    if props.get('parking_yn') == 'Y': score += 4
    return min(30, score)

def calculate_scale_score(prop_type, star_rating):
    """
    Max 20 points
    """
    score = 5
    if prop_type == 'hotel': score += 5
    if star_rating and star_rating >= 4: score += 10
    elif star_rating and star_rating >= 3: score += 5
    return min(20, score)

def get_internal_grade(total_score):
    if total_score >= 85: return "Premium"
    if total_score >= 70: return "Upper-mid"
    if total_score >= 55: return "Standard"
    return "Budget"

def grade_property(prop_data):
    # 1. Location (Real Coords)
    loc_score = calculate_location_score(prop_data.get('raw_lat'), prop_data.get('raw_lng'))
    
    # 2. Review
    rev_score = calculate_review_score_component(
        prop_data.get('review_score_std', 0),
        prop_data.get('review_count', 0)
    )
    
    # 3. Facility
    fac_score = calculate_facility_score(prop_data)
    
    # 4. Scale
    scale_score = calculate_scale_score(
        prop_data.get('property_type_std'),
        prop_data.get('official_star_rating')
    )
    
    total = loc_score + rev_score + fac_score + scale_score
    grade = get_internal_grade(total)
    
    return {
        "location_score": loc_score,
        "review_score_component": rev_score,
        "facility_score": fac_score,
        "scale_score": scale_score,
        "total_grade_score": total,
        "internal_grade": grade,
        "note": f"L:{loc_score} F:{fac_score} R:{rev_score} S:{scale_score}"
    }
