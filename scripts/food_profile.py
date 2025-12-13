"""
EQ12 FOOD INTELLIGENCE - TASTE PROFILE & SCORING ENGINE
Free-tier location intelligence for food recommendations
Uses: OpenStreetMap (100% free) + OpenRouteService (free tier)
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import json

@dataclass
class FoodProfile:
    """User taste preferences and constraints"""
    favorite_cuisines: List[str]  # ["Jamaican", "Italian", "Soul Food"]
    avoid_cuisines: List[str]     # ["Sushi", "Raw"]
    max_distance_km: float         # 5.0 = 5km radius
    min_price_level: int           # 1 = cheap, 4 = high-end
    max_price_level: int
    spice_tolerance: int           # 1-5 scale
    late_night_ok: bool
    healthy_bias: float            # 0.0-1.0 (0 = no preference, 1 = very healthy)
    dietary_restrictions: List[str] = None  # ["halal", "vegetarian", "gluten-free"]
    
    def to_json(self) -> str:
        """Serialize to JSON for VB.NET bridge"""
        return json.dumps(asdict(self))
    
    @classmethod
    def from_json(cls, json_str: str) -> 'FoodProfile':
        """Deserialize from JSON (from VB.NET)"""
        data = json.loads(json_str)
        return cls(**data)


def score_restaurant(rest: Dict, profile: FoodProfile) -> float:
    """
    Score a restaurant based on user profile
    
    Args:
        rest: Restaurant dict from API with keys:
              {name, cuisines, price_level, distance_km, rating, open_now, 
               address, url, dietary_options}
        profile: User FoodProfile
    
    Returns:
        Score (higher = better match). Range: -10 to +20
    """
    score = 0.0
    
    # CUISINE MATCH (most important)
    cuisines = [c.lower() for c in rest.get("cuisines", [])]
    
    # Favorite cuisine bonus
    if any(c in cuisines for c in [fc.lower() for fc in profile.favorite_cuisines]):
        score += 5.0  # Strong bonus
    
    # Avoid cuisine penalty
    if any(c in cuisines for c in [ac.lower() for ac in profile.avoid_cuisines]):
        score -= 10.0  # Strong penalty (knockout)
    
    # DISTANCE PENALTY
    dist = rest.get("distance_km", 999)
    if dist > profile.max_distance_km:
        score -= 5.0  # Too far
    else:
        # Closer = better (inverse distance bonus)
        score += max(0, (profile.max_distance_km - dist) / profile.max_distance_km * 2.0)
    
    # PRICE ALIGNMENT
    price = rest.get("price_level", 2)
    if price < profile.min_price_level or price > profile.max_price_level:
        score -= 3.0  # Out of budget range
    else:
        score += 1.0  # Good price match
    
    # RATING BONUS
    rating = rest.get("rating", 3.5)
    score += (rating - 3.5)  # Above-average gets bonus
    
    # HEALTH BIAS
    if profile.healthy_bias > 0:
        # Check for healthy keywords
        healthy_keywords = ["salad", "bowl", "fresh", "organic", "vegetarian", "vegan"]
        if any(kw in " ".join(cuisines) for kw in healthy_keywords):
            score += 3.0 * profile.healthy_bias
    
    # LATE NIGHT BONUS
    if profile.late_night_ok and rest.get("open_late", False):
        score += 1.5
    
    # DIETARY RESTRICTIONS (critical)
    if profile.dietary_restrictions:
        rest_options = [opt.lower() for opt in rest.get("dietary_options", [])]
        for restriction in profile.dietary_restrictions:
            if restriction.lower() not in rest_options:
                score -= 5.0  # Missing critical dietary option
    
    # SPICE TOLERANCE
    if "spicy" in " ".join(cuisines).lower():
        if profile.spice_tolerance < 3:
            score -= 2.0  # Too spicy for user
    
    return score


def create_default_profile(zip_code: str = "14215") -> FoodProfile:
    """Create default profile for Buffalo NY 14215"""
    return FoodProfile(
        favorite_cuisines=["Jamaican", "Soul Food", "Italian", "Mexican"],
        avoid_cuisines=["Sushi", "Raw"],
        max_distance_km=5.0,  # 5km radius
        min_price_level=1,
        max_price_level=2,  # Cheap to moderate
        spice_tolerance=4,
        late_night_ok=True,
        healthy_bias=0.3,  # Slight preference for healthier
        dietary_restrictions=["halal"]  # Example
    )


if __name__ == "__main__":
    # Example usage
    profile = create_default_profile()
    print("Default Food Profile:")
    print(json.dumps(asdict(profile), indent=2))
    
    # Test restaurant scoring
    test_restaurant = {
        "name": "Island Vibes Jamaican Kitchen",
        "cuisines": ["Jamaican", "Caribbean"],
        "price_level": 2,
        "distance_km": 2.5,
        "rating": 4.3,
        "open_now": True,
        "open_late": True,
        "dietary_options": ["halal", "vegetarian"],
        "address": "123 Main St, Buffalo NY 14215"
    }
    
    score = score_restaurant(test_restaurant, profile)
    print(f"\nTest Restaurant Score: {score:.2f}")
    print(f"Restaurant: {test_restaurant['name']}")
