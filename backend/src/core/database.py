"""
Geo utilities and lightweight domain types used across the codebase.

The algorithmic structures (RedditFeed heap, CommentTree DFS, SpatialIndex,
LocationRecommendationEngine) have been factored into their respective services
so that they operate on DB-loaded data instead of in-memory state.
"""
import math
from dataclasses import dataclass
from typing import Literal, Optional


# =============================================================================
# GEOSPATIAL UTILITIES
# =============================================================================

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def geohash_encode(lat: float, lon: float, precision: int = 6) -> str:
    base32 = "0123456789bcdefghjkmnpqrstuvwxyz"
    lat_range, lon_range = [-90.0, 90.0], [-180.0, 180.0]
    geohash, bits, bit, even = [], 0, 0, True
    while len(geohash) < precision:
        if even:
            mid = (lon_range[0] + lon_range[1]) / 2
            if lon > mid:
                bit |= (1 << (4 - bits)); lon_range[0] = mid
            else:
                lon_range[1] = mid
        else:
            mid = (lat_range[0] + lat_range[1]) / 2
            if lat > mid:
                bit |= (1 << (4 - bits)); lat_range[0] = mid
            else:
                lat_range[1] = mid
        even = not even
        bits += 1
        if bits == 5:
            geohash.append(base32[bit]); bits = 0; bit = 0
    return "".join(geohash)


# =============================================================================
# LIGHTWEIGHT DOMAIN TYPES
# =============================================================================

@dataclass
class Location:
    latitude: float
    longitude: float
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    geohash: Optional[str] = None

    def __post_init__(self):
        if not self.geohash:
            self.geohash = geohash_encode(self.latitude, self.longitude)

    def distance_to(self, other: "Location") -> float:
        return haversine_distance(self.latitude, self.longitude, other.latitude, other.longitude)


@dataclass
class LocationScope:
    scope_type: Literal["city", "region", "country", "global"]
    location: Optional[Location] = None
    radius_km: Optional[float] = None


@dataclass
class SubredditRecommendation:
    subreddit_id: int
    subreddit_name: str
    total_score: float
    distance_km: Optional[float]
    distance_score: float
    activity_score: float
    relevance_score: float
    reason: str
