from thefuzz import fuzz
from .normalize import normalize_name, normalize_address
from .geo_match import calculate_distance, get_geo_score

def calculate_match_score(target, candidate):
    """
    target: {name, address, lat, lng, type}
    candidate: {name, address, lat, lng, type}
    
    Returns: score (int), details (dict)
    """
    score = 0
    details = {}
    
    # 1. Geo Score
    dist = calculate_distance(target.get('lat'), target.get('lng'), 
                              candidate.get('lat'), candidate.get('lng'))
    geo_score = get_geo_score(dist)
    score += geo_score
    details['geo'] = geo_score
    details['distance_m'] = dist
    
    # 2. Name Similarity
    norm_target_name = normalize_name(target.get('name', ''))
    norm_cand_name = normalize_name(candidate.get('name', ''))
    
    name_sim = fuzz.token_sort_ratio(norm_target_name, norm_cand_name)
    name_score = 20 if name_sim >= 85 else (10 if name_sim >= 70 else 0)
    score += name_score
    details['name'] = name_score
    details['name_sim'] = name_sim
    
    # 3. Address Similarity
    addr_sim = fuzz.partial_ratio(normalize_address(target.get('address', '')), 
                                  normalize_address(candidate.get('address', '')))
    addr_score = 25 if addr_sim >= 90 else (15 if addr_sim >= 75 else 0)
    score += addr_score
    details['address'] = addr_score
    details['address_sim'] = addr_sim
    
    # 4. Type Match
    type_score = 0
    if target.get('type') and candidate.get('type'):
        if target.get('type') == candidate.get('type'):
            type_score = 10
    score += type_score
    details['type'] = type_score
    
    return score, details

def determine_status(score):
    if score >= 80:
        return "confirmed"
    elif score >= 60:
        return "review_needed"
    else:
        return "unmatched"
