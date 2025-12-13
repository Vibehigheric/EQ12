"""
EQ12 RESTAURANT FINDER - FREE TIER LOCATION ENGINE
Uses 100% free services:
- OpenStreetMap (OSM) - map data + POI
- Nominatim - geocoding (address → lat/lon)
- OpenRouteService - routing + isochrones
- OSMNX Python library - restaurant queries
"""

import os
import sys
import json
import logging
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from datetime import datetime

# Import from food_profile
sys.path.insert(0, str(Path(__file__).parent))
from food_profile import FoodProfile, score_restaurant

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def fetch_restaurants_osm(lat: float, lon: float, radius_m: int = 3000) -> List[Dict]:
    """
    Fetch restaurants using OpenStreetMap (100% free)
    
    Args:
        lat: Latitude
        lon: Longitude  
        radius_m: Search radius in meters (default 3km)
    
    Returns:
        List of restaurants with standardized format
    """
    try:
        import osmnx as ox
        import pandas as pd
    except ImportError:
        logger.error("osmnx not installed. Run: pip install osmnx")
        return []
    
    try:
        # Query OSM for restaurants
        tags = {"amenity": "restaurant"}
        restaurants_gdf = ox.features_from_point((lat, lon), tags, dist=radius_m)
        
        # Standardize format
        results = []
        for idx, row in restaurants_gdf.iterrows():
            # Extract data
            name = row.get("name", "Unknown Restaurant")
            cuisine = row.get("cuisine", "").split(";") if row.get("cuisine") else []
            
            # Calculate distance
            from geopy.distance import geodesic
            rest_lat = row.geometry.centroid.y
            rest_lon = row.geometry.centroid.x
            distance_km = geodesic((lat, lon), (rest_lat, rest_lon)).km
            
            # Price level (OSM doesn't have this, use heuristic)
            price_level = 2  # Default moderate
            
            # Rating (OSM doesn't have, use placeholder)
            rating = 3.8  # Default
            
            # Standardized restaurant dict
            restaurant = {
                "name": name,
                "cuisines": cuisine,
                "price_level": price_level,
                "distance_km": round(distance_km, 2),
                "rating": rating,
                "open_now": True,  # OSM doesn't track hours easily
                "open_late": False,
                "address": row.get("addr:street", "Address not available"),
                "url": f"https://www.openstreetmap.org/{row.get('osm_id', '')}",
                "dietary_options": [],  # OSM doesn't track this
                "lat": rest_lat,
                "lon": rest_lon
            }
            results.append(restaurant)
        
        logger.info(f"Found {len(results)} restaurants from OSM")
        return results
    
    except Exception as e:
        logger.error(f"Error fetching from OSM: {e}")
        return []


def geocode_address(address: str) -> Optional[Tuple[float, float]]:
    """
    Convert address to coordinates using Nominatim (free)
    
    Args:
        address: Street address or ZIP code
    
    Returns:
        (lat, lon) tuple or None if failed
    """
    try:
        from geopy.geocoders import Nominatim
        geolocator = Nominatim(user_agent="eq12_food_finder")
        location = geolocator.geocode(address)
        
        if location:
            logger.info(f"Geocoded '{address}' to ({location.latitude}, {location.longitude})")
            return (location.latitude, location.longitude)
        else:
            logger.warning(f"Could not geocode address: {address}")
            return None
    
    except Exception as e:
        logger.error(f"Geocoding error: {e}")
        return None


def recommend_restaurants(
    profile: FoodProfile,
    location: str = "14215",  # Can be address or ZIP
    top_n: int = 5
) -> List[Tuple[float, Dict]]:
    """
    Generate top N restaurant recommendations
    
    Args:
        profile: User FoodProfile
        location: Address or ZIP code
        top_n: Number of recommendations to return
    
    Returns:
        List of (score, restaurant_dict) tuples, sorted by score (descending)
    """
    # Geocode location
    coords = geocode_address(location)
    if not coords:
        logger.error("Failed to geocode location")
        return []
    
    lat, lon = coords
    radius_m = int(profile.max_distance_km * 1000)  # km to meters
    
    # Fetch restaurants
    restaurants = fetch_restaurants_osm(lat, lon, radius_m)
    if not restaurants:
        logger.warning("No restaurants found")
        return []
    
    # Score each restaurant
    scored = []
    for rest in restaurants:
        rest_score = score_restaurant(rest, profile)
        scored.append((rest_score, rest))
    
    # Sort by score (descending)
    scored.sort(key=lambda x: x[0], reverse=True)
    
    logger.info(f"Scored {len(scored)} restaurants, returning top {top_n}")
    return scored[:top_n]


def format_recommendation(score: float, restaurant: Dict) -> str:
    """Format a single recommendation for display"""
    return f"""
🍽️  {restaurant['name']} (Score: {score:.1f}/10)
   Cuisines: {', '.join(restaurant['cuisines'])}
   Distance: {restaurant['distance_km']} km
   Price: {'$' * restaurant['price_level']}
   Rating: {'⭐' * int(restaurant['rating'])} ({restaurant['rating']})
   Address: {restaurant['address']}
"""


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="EQ12 Food Finder - Free Tier Location Engine")
    parser.add_argument("--location", default="14215", help="Address or ZIP code")
    parser.add_argument("--cuisines", default="Jamaican,Soul Food,Italian", help="Favorite cuisines (comma-separated)")
    parser.add_argument("--distance", type=float, default=5.0, help="Max distance in km")
    parser.add_argument("--top", type=int, default=5, help="Number of recommendations")
    
    args = parser.parse_args()
    
    # Create profile from args
    profile = FoodProfile(
        favorite_cuisines=args.cuisines.split(","),
        avoid_cuisines=["Sushi"],
        max_distance_km=args.distance,
        min_price_level=1,
        max_price_level=2,
        spice_tolerance=4,
        late_night_ok=True,
        healthy_bias=0.3,
        dietary_restrictions=[]
    )
    
    logger.info(f"Searching for restaurants near {args.location}")
    logger.info(f"Favorite cuisines: {', '.join(profile.favorite_cuisines)}")
    
    # Get recommendations
    recommendations = recommend_restaurants(profile, args.location, args.top)
    
    if recommendations:
        print("\n" + "="*60)
        print(f"🎯 TOP {len(recommendations)} FOOD RECOMMENDATIONS")
        print("="*60)
        
        for score, rest in recommendations:
            print(format_recommendation(score, rest))
        
        # Save to JSON
        output_file = Path(__file__).parent.parent / "logs" / f"food_recommendations_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump([{"score": score, **rest} for score, rest in recommendations], f, indent=2)
        
        logger.info(f"Saved recommendations to {output_file}")
    else:
        logger.error("No recommendations found")
