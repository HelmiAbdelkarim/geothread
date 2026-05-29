import heapq
import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Literal, Optional, Set, Tuple

from src.algorithms.tree import CommentTree


# =============================================================================
# GEOSPATIAL UTILITIES
# =============================================================================

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    lat1_r = math.radians(lat1)
    lat2_r = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def geohash_encode(lat: float, lon: float, precision: int = 6) -> str:
    base32 = "0123456789bcdefghjkmnpqrstuvwxyz"
    lat_range = [-90.0, 90.0]
    lon_range = [-180.0, 180.0]
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
# DOMAIN MODELS
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

    def contains(self, user_location: Location) -> bool:
        if self.scope_type == "global":
            return True
        if not self.location or not user_location:
            return False
        if self.scope_type == "city" and self.radius_km:
            return self.location.distance_to(user_location) <= self.radius_km
        if self.scope_type == "region":
            return (self.location.region == user_location.region
                    and self.location.country == user_location.country)
        if self.scope_type == "country":
            return self.location.country == user_location.country
        return False


@dataclass
class Redditor:
    user_id: int
    username: str
    email: str
    created_at: datetime
    post_karma: int = 0
    comment_karma: int = 0
    location: Optional[Location] = None

    @property
    def total_karma(self) -> int:
        return self.post_karma + self.comment_karma

    def __hash__(self):
        return hash(self.user_id)

    def __eq__(self, other):
        return isinstance(other, Redditor) and self.user_id == other.user_id


@dataclass
class Subreddit:
    subreddit_id: int
    name: str
    description: str
    created_at: datetime
    topic: Optional[str] = None
    subscriber_count: int = 0
    location_scope: Optional[LocationScope] = None
    activity_score: float = 0.0

    def __hash__(self):
        return hash(self.subreddit_id)

    def is_relevant_for_location(self, user_location: Location) -> bool:
        if not self.location_scope:
            return True
        return self.location_scope.contains(user_location)

    def distance_to_user(self, user_location: Location) -> Optional[float]:
        if not self.location_scope or not self.location_scope.location:
            return None
        return self.location_scope.location.distance_to(user_location)


@dataclass
class Post:
    post_id: int
    author_id: int
    subreddit_id: int
    title: str
    content: str
    timestamp: datetime
    upvotes: int = 0
    downvotes: int = 0
    comments: int = 0
    share_count: int = 0
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    @property
    def score(self) -> int:
        return self.upvotes - self.downvotes

    @property
    def vote_ratio(self) -> float:
        total = self.upvotes + self.downvotes
        return self.upvotes / total if total else 0.5

    @property
    def location(self) -> Optional[Location]:
        if self.latitude is None or self.longitude is None:
            return None
        return Location(self.latitude, self.longitude)

    def calculate_hot_score(self) -> float:
        score = self.score
        order = math.log10(max(abs(score), 1))
        sign = 1 if score > 0 else (-1 if score < 0 else 0)
        seconds = (self.timestamp - datetime(1970, 1, 1)).total_seconds()
        return round(sign * order + seconds / 45000, 7)

    def calculate_controversial_score(self) -> float:
        if not self.upvotes or not self.downvotes:
            return 0.0
        magnitude = self.upvotes + self.downvotes
        balance = min(self.upvotes, self.downvotes) / max(self.upvotes, self.downvotes)
        return magnitude * balance

    def calculate_priority(self, strategy: Literal["hot", "new", "top", "rising", "controversial"] = "hot") -> float:
        if strategy == "hot":
            return self.calculate_hot_score()
        if strategy == "new":
            return (self.timestamp - datetime(1970, 1, 1)).total_seconds()
        if strategy == "top":
            return float(self.score)
        if strategy == "rising":
            age_hours = (datetime.now() - self.timestamp).total_seconds() / 3600
            return 0.0 if age_hours > 24 else self.score / (age_hours + 2) ** 1.5
        if strategy == "controversial":
            return self.calculate_controversial_score()
        return 0.0


@dataclass
class Comment:
    comment_id: int
    content: str
    author_id: int
    post_id: int
    parent_comment_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    is_edited: bool = False
    is_deleted: bool = False
    upvotes: int = 0
    downvotes: int = 0

    @property
    def score(self) -> int:
        return self.upvotes - self.downvotes

    def to_dict(self) -> Dict:
        return {
            "comment_id": self.comment_id,
            "content": self.content if not self.is_deleted else "[deleted]",
            "author_id": self.author_id if not self.is_deleted else None,
            "post_id": self.post_id,
            "parent_comment_id": self.parent_comment_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_edited": self.is_edited,
            "is_deleted": self.is_deleted,
            "upvotes": self.upvotes,
            "downvotes": self.downvotes,
            "score": self.score,
        }


# =============================================================================
# STORAGE INTERNALS
# =============================================================================

class RedditorNode:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.subscribed_subreddits: Set[int] = set()
        self.created_at: Optional[datetime] = None

    def subscribe(self, subreddit_id: int) -> None:
        self.subscribed_subreddits.add(subreddit_id)

    def unsubscribe(self, subreddit_id: int) -> None:
        self.subscribed_subreddits.discard(subreddit_id)

    def is_subscribed(self, subreddit_id: int) -> bool:
        return subreddit_id in self.subscribed_subreddits

    @property
    def subscription_count(self) -> int:
        return len(self.subscribed_subreddits)


class RedditorStorage:
    def __init__(self):
        self._by_id: Dict[int, Redditor] = {}
        self._by_username: Dict[str, Redditor] = {}
        self._by_email: Dict[str, Redditor] = {}

    def add(self, user: Redditor) -> bool:
        if user.user_id in self._by_id:
            return False
        self._by_id[user.user_id] = user
        self._by_username[user.username] = user
        self._by_email[user.email] = user
        return True

    def get_by_id(self, user_id: int) -> Optional[Redditor]:
        return self._by_id.get(user_id)

    def get_by_username(self, username: str) -> Optional[Redditor]:
        return self._by_username.get(username)

    def get_all(self) -> List[Redditor]:
        return list(self._by_id.values())

    def exists(self, user_id: int) -> bool:
        return user_id in self._by_id


# =============================================================================
# FEED (max-heap priority queue)
# =============================================================================

class RedditFeed:
    def __init__(self, user_id: int, sort: str = "hot"):
        self.user_id = user_id
        self.sort = sort
        self._heap: List[Tuple] = []
        self.post_ids: Set[int] = set()

    def add_post(self, post: Post) -> None:
        if post.post_id in self.post_ids:
            return
        priority = post.calculate_priority(self.sort)
        heapq.heappush(self._heap, (-priority, post.timestamp, post.post_id, post))
        self.post_ids.add(post.post_id)

    def get_top_posts(self, n: int = 25, offset: int = 0) -> List[Post]:
        ranked = sorted(self._heap, key=lambda x: (x[0], -x[1].timestamp(), x[2]))
        return [item[3] for item in ranked[offset:offset + n]]

    def remove_post(self, post_id: int) -> None:
        if post_id not in self.post_ids:
            return
        self._heap = [item for item in self._heap if item[2] != post_id]
        heapq.heapify(self._heap)
        self.post_ids.discard(post_id)

    def refresh_priorities(self, posts: Dict[int, Post]) -> None:
        post_list = [item[3] for item in self._heap]
        self._heap = []
        self.post_ids.clear()
        for post in post_list:
            self.add_post(posts.get(post.post_id, post))

    def change_sort(self, new_sort: str, posts: Dict[int, Post]) -> None:
        self.sort = new_sort
        self.refresh_priorities(posts)

    def size(self) -> int:
        return len(self._heap)


# =============================================================================
# SPATIAL INDEX
# =============================================================================

class SpatialIndex:
    def __init__(self):
        self._buckets: Dict[str, List[int]] = {}
        self._geohashes: Dict[int, str] = {}

    def add_subreddit(self, subreddit_id: int, location: Location) -> None:
        gh = location.geohash
        self._buckets.setdefault(gh, []).append(subreddit_id)
        self._geohashes[subreddit_id] = gh

    def remove_subreddit(self, subreddit_id: int) -> None:
        gh = self._geohashes.pop(subreddit_id, None)
        if gh and gh in self._buckets:
            self._buckets[gh].remove(subreddit_id)

    def find_nearby(self, location: Location, precision: int = 6) -> List[int]:
        gh = geohash_encode(location.latitude, location.longitude, precision)
        nearby = list(self._buckets.get(gh, []))
        prefix = gh[:-1] if len(gh) > 1 else ""
        for bucket_gh, ids in self._buckets.items():
            if bucket_gh.startswith(prefix) and bucket_gh != gh:
                nearby.extend(ids)
        return list(set(nearby))


# =============================================================================
# RECOMMENDATION ENGINE
# =============================================================================

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


class LocationRecommendationEngine:
    def __init__(self, reddit: "RedditSystem"):
        self.reddit = reddit

    def calculate_distance_score(self, distance_km: Optional[float]) -> float:
        if distance_km is None:
            return 0.5
        return max(0.0, min(1.0, math.exp(-0.01 * distance_km)))

    def calculate_activity_score(self, subreddit: Subreddit) -> float:
        posts = self.reddit.get_subreddit_posts(subreddit.subreddit_id)
        if not posts:
            return 0.0
        now = datetime.now()
        recent = [p for p in posts if (now - p.timestamp).days <= 30]
        score = min(1.0, len(recent) / 30.0 / 10.0)
        if subreddit.subscriber_count > 0:
            score = (score + math.log10(subreddit.subscriber_count + 1) / 6.0) / 2.0
        return score

    def calculate_relevance_score(self, user_id: int, subreddit: Subreddit) -> float:
        node = self.reddit.nodes.get(user_id)
        if not node:
            return 0.5
        if node.is_subscribed(subreddit.subreddit_id):
            return 0.0
        subscriptions = self.reddit.get_subscriptions(user_id)
        if not subscriptions:
            return 0.5
        interests = set()
        subscribed_topics = set()
        for sub in subscriptions:
            interests.update(sub.name.lower().split("_"))
            if sub.topic:
                subscribed_topics.add(sub.topic.lower())
        if subreddit.topic and subreddit.topic.lower() in subscribed_topics:
            return 0.9
        return 0.8 if interests & set(subreddit.name.lower().split("_")) else 0.3

    def recommend(self, user_id: int, limit: int = 10, max_distance_km: float = 100.0) -> List[SubredditRecommendation]:
        user = self.reddit.get_user(user_id)
        if not user or not user.location:
            return self._fallback(user_id, limit)

        node = self.reddit.nodes.get(user_id)
        results = []
        for subreddit in self.reddit.subreddits.values():
            if not subreddit.location_scope:
                continue
            if node and node.is_subscribed(subreddit.subreddit_id):
                continue
            distance = subreddit.distance_to_user(user.location)
            if distance and distance > max_distance_km:
                continue
            d = self.calculate_distance_score(distance)
            a = self.calculate_activity_score(subreddit)
            r = self.calculate_relevance_score(user_id, subreddit)
            results.append(SubredditRecommendation(
                subreddit_id=subreddit.subreddit_id,
                subreddit_name=subreddit.name,
                total_score=d * 0.4 + a * 0.3 + r * 0.3,
                distance_km=distance,
                distance_score=d,
                activity_score=a,
                relevance_score=r,
                reason=self._reason(subreddit, distance, a, r),
            ))
        results.sort(key=lambda x: x.total_score, reverse=True)
        return results[:limit]

    def _reason(self, subreddit: Subreddit, distance: Optional[float], activity: float, relevance: float) -> str:
        parts = []
        if distance is not None:
            parts.append(f"Very close ({distance:.1f} km away)" if distance < 10 else f"Nearby ({distance:.1f} km away)" if distance < 50 else "")
        if activity > 0.7:
            parts.append("Very active community")
        elif activity > 0.4:
            parts.append("Active community")
        if relevance > 0.7:
            parts.append("Matches your interests")
        if subreddit.subscriber_count > 10000:
            parts.append(f"{subreddit.subscriber_count:,} members")
        return " • ".join(p for p in parts if p) or "Popular in your area"

    def _fallback(self, user_id: int, limit: int) -> List[SubredditRecommendation]:
        node = self.reddit.nodes.get(user_id)
        results = []
        for subreddit in self.reddit.subreddits.values():
            if node and node.is_subscribed(subreddit.subreddit_id):
                continue
            a = self.calculate_activity_score(subreddit)
            r = self.calculate_relevance_score(user_id, subreddit)
            results.append(SubredditRecommendation(
                subreddit_id=subreddit.subreddit_id, subreddit_name=subreddit.name,
                total_score=a * 0.5 + r * 0.5, distance_km=None,
                distance_score=0.0, activity_score=a, relevance_score=r,
                reason="Popular community",
            ))
        results.sort(key=lambda x: x.total_score, reverse=True)
        return results[:limit]


# =============================================================================
# REDDIT SYSTEM (in-memory store)
# =============================================================================

class RedditSystem:
    def __init__(self, default_sort: str = "hot"):
        self.users = RedditorStorage()
        self.nodes: Dict[int, RedditorNode] = {}

        self.subreddits: Dict[int, Subreddit] = {}
        self._subreddits_by_name: Dict[str, Subreddit] = {}

        self.posts: Dict[int, Post] = {}
        self._subreddit_posts: Dict[int, List[int]] = {}
        self._user_posts: Dict[int, List[int]] = {}

        self._feeds: Dict[int, RedditFeed] = {}
        self._user_sorts: Dict[int, str] = {}
        self._post_votes: Dict[int, Dict[int, int]] = {}
        self._post_shares: Dict[int, Dict[int, int]] = {}

        self.comments: Dict[int, Comment] = {}
        self._comment_trees: Dict[int, CommentTree] = {}
        self._comment_votes: Dict[int, Dict[int, int]] = {}

        self._next_user_id = 1
        self._next_subreddit_id = 1
        self._next_post_id = 1
        self._next_comment_id = 1

        self.default_sort = default_sort
        self.spatial_index = SpatialIndex()
        self.recommendation_engine = LocationRecommendationEngine(self)

    # -------------------------------------------------------------------------
    # Users
    # -------------------------------------------------------------------------

    def create_user(self, username: str, email: str, sort: Optional[str] = None, location: Optional[Location] = None) -> Redditor:
        user = Redditor(user_id=self._next_user_id, username=username, email=email, created_at=datetime.now(), location=location)
        self._next_user_id += 1
        node = RedditorNode(user.user_id)
        node.created_at = datetime.now()
        self.users.add(user)
        self.nodes[user.user_id] = node
        self._user_posts[user.user_id] = []
        self._post_votes[user.user_id] = {}
        user_sort = sort or self.default_sort
        self._feeds[user.user_id] = RedditFeed(user.user_id, user_sort)
        self._user_sorts[user.user_id] = user_sort
        self._post_shares[user.user_id] = {}
        return user

    def get_user(self, user_id: int) -> Optional[Redditor]:
        return self.users.get_by_id(user_id)

    def get_user_by_username(self, username: str) -> Optional[Redditor]:
        return self.users.get_by_username(username)

    def update_user_location(self, user_id: int, location: Location) -> bool:
        user = self.get_user(user_id)
        if not user:
            return False
        user.location = location
        return True

    def get_user_stats(self, user_id: int) -> Optional[Dict]:
        user = self.users.get_by_id(user_id)
        node = self.nodes.get(user_id)
        if not user or not node:
            return None
        feed = self._feeds.get(user_id)
        return {
            "user_id": user_id,
            "username": user.username,
            "post_karma": user.post_karma,
            "comment_karma": user.comment_karma,
            "total_karma": user.total_karma,
            "subscriptions": node.subscription_count,
            "posts_created": len(self._user_posts.get(user_id, [])),
            "feed_size": feed.size() if feed else 0,
            "feed_sort": self._user_sorts.get(user_id),
        }

    # -------------------------------------------------------------------------
    # Subreddits
    # -------------------------------------------------------------------------

    def create_subreddit(
        self,
        name: str,
        description: str,
        location_scope: Optional[LocationScope] = None,
        topic: Optional[str] = None,
    ) -> Subreddit:
        subreddit = Subreddit(
            subreddit_id=self._next_subreddit_id,
            name=name,
            description=description,
            created_at=datetime.now(),
            topic=topic.strip() if topic else None,
            location_scope=location_scope,
        )
        self._next_subreddit_id += 1
        self.subreddits[subreddit.subreddit_id] = subreddit
        self._subreddits_by_name[name.lower()] = subreddit
        self._subreddit_posts[subreddit.subreddit_id] = []
        if location_scope and location_scope.location:
            self.spatial_index.add_subreddit(subreddit.subreddit_id, location_scope.location)
        return subreddit

    def get_subreddit(self, subreddit_id: int) -> Optional[Subreddit]:
        return self.subreddits.get(subreddit_id)

    def get_subreddit_by_name(self, name: str) -> Optional[Subreddit]:
        return self._subreddits_by_name.get(name.lower())

    def get_all_subreddits(self) -> List[Subreddit]:
        return list(self.subreddits.values())

    def subscribe(self, user_id: int, subreddit_id: int) -> bool:
        node = self.nodes.get(user_id)
        subreddit = self.subreddits.get(subreddit_id)
        if not node or not subreddit:
            return False
        node.subscribe(subreddit_id)
        subreddit.subscriber_count += 1
        self._populate_feed(user_id, subreddit_id)
        return True

    def unsubscribe(self, user_id: int, subreddit_id: int) -> bool:
        node = self.nodes.get(user_id)
        subreddit = self.subreddits.get(subreddit_id)
        if not node or not subreddit:
            return False
        node.unsubscribe(subreddit_id)
        subreddit.subscriber_count -= 1
        self._remove_feed_posts(user_id, subreddit_id)
        return True

    def is_subscribed(self, user_id: int, subreddit_id: int) -> bool:
        node = self.nodes.get(user_id)
        return node.is_subscribed(subreddit_id) if node else False

    def get_subscriptions(self, user_id: int) -> List[Subreddit]:
        node = self.nodes.get(user_id)
        if not node:
            return []
        return [self.subreddits[sid] for sid in node.subscribed_subreddits if sid in self.subreddits]

    def get_online_count(self, subreddit_id: int, active_window_hours: int = 24) -> int:
        if subreddit_id not in self.subreddits:
            return 0
        cutoff = datetime.now() - timedelta(hours=active_window_hours)
        active_user_ids: Set[int] = set()

        post_ids = set(self._subreddit_posts.get(subreddit_id, []))
        for post_id in post_ids:
            post = self.posts.get(post_id)
            if post and post.timestamp >= cutoff:
                active_user_ids.add(post.author_id)

        for comment in self.comments.values():
            if comment.post_id in post_ids and comment.created_at >= cutoff and not comment.is_deleted:
                active_user_ids.add(comment.author_id)

        return sum(
            1
            for user_id in active_user_ids
            if self.nodes.get(user_id) and self.nodes[user_id].is_subscribed(subreddit_id)
        )

    # -------------------------------------------------------------------------
    # Posts
    # -------------------------------------------------------------------------

    def create_post(
        self,
        author_id: int,
        subreddit_id: int,
        title: str,
        content: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> Optional[Post]:
        if not self.users.exists(author_id) or subreddit_id not in self.subreddits:
            return None
        if (latitude is None) != (longitude is None):
            return None
        post = Post(
            post_id=self._next_post_id,
            author_id=author_id,
            subreddit_id=subreddit_id,
            title=title,
            content=content,
            timestamp=datetime.now(),
            latitude=latitude,
            longitude=longitude,
        )
        self._next_post_id += 1
        self.posts[post.post_id] = post
        self._subreddit_posts[subreddit_id].append(post.post_id)
        self._user_posts[author_id].append(post.post_id)
        for user_id, node in self.nodes.items():
            if node.is_subscribed(subreddit_id):
                feed = self._feeds.get(user_id)
                if feed:
                    feed.add_post(post)
        return post

    def get_post(self, post_id: int) -> Optional[Post]:
        return self.posts.get(post_id)

    def get_subreddit_posts(self, subreddit_id: int) -> List[Post]:
        return [self.posts[pid] for pid in self._subreddit_posts.get(subreddit_id, []) if pid in self.posts]

    def get_user_posts(self, user_id: int) -> List[Post]:
        return [self.posts[pid] for pid in self._user_posts.get(user_id, []) if pid in self.posts]

    def get_feed(self, user_id: int, count: int = 25, offset: int = 0) -> List[Post]:
        feed = self._feeds.get(user_id)
        return feed.get_top_posts(count, offset) if feed else []

    def get_feed_count(self, user_id: int) -> int:
        feed = self._feeds.get(user_id)
        return feed.size() if feed else 0

    def get_closest_feed(
        self,
        user_id: int,
        count: int = 25,
        radius_km: Optional[float] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> List[Tuple[Post, float]]:
        if (latitude is None) != (longitude is None):
            return []
        if latitude is not None and longitude is not None:
            origin = Location(latitude, longitude)
        else:
            user = self.get_user(user_id)
            if not user or not user.location:
                return []
            origin = user.location

        node = self.nodes.get(user_id)
        if not node:
            return []

        ranked: List[Tuple[float, Post]] = []
        for subreddit_id in node.subscribed_subreddits:
            for post_id in self._subreddit_posts.get(subreddit_id, []):
                post = self.posts.get(post_id)
                post_location = post.location if post else None
                if not post or not post_location:
                    continue
                distance = origin.distance_to(post_location)
                if radius_km is not None and distance > radius_km:
                    continue
                ranked.append((distance, post))

        ranked.sort(key=lambda item: (item[0], item[1].timestamp), reverse=False)
        return [(post, distance) for distance, post in ranked[:count]]

    def get_user_sort(self, user_id: int) -> Optional[str]:
        return self._user_sorts.get(user_id)

    def change_feed_sort(self, user_id: int, sort: str) -> bool:
        feed = self._feeds.get(user_id)
        if not feed:
            return False
        feed.change_sort(sort, self.posts)
        self._user_sorts[user_id] = sort
        return True

    # -------------------------------------------------------------------------
    # Post votes
    # -------------------------------------------------------------------------

    def upvote_post(self, post_id: int, user_id: int) -> bool:
        post = self.posts.get(post_id)
        if not post or not self.users.exists(user_id):
            return False
        current = self._post_votes[user_id].get(post_id, 0)
        if current == 1:
            post.upvotes -= 1; self._post_votes[user_id][post_id] = 0
        elif current == -1:
            post.downvotes -= 1; post.upvotes += 1; self._post_votes[user_id][post_id] = 1
        else:
            post.upvotes += 1; self._post_votes[user_id][post_id] = 1
        self._recalc_post_karma(post.author_id)
        self._refresh_post(post_id)
        return True

    def downvote_post(self, post_id: int, user_id: int) -> bool:
        post = self.posts.get(post_id)
        if not post or not self.users.exists(user_id):
            return False
        current = self._post_votes[user_id].get(post_id, 0)
        if current == -1:
            post.downvotes -= 1; self._post_votes[user_id][post_id] = 0
        elif current == 1:
            post.upvotes -= 1; post.downvotes += 1; self._post_votes[user_id][post_id] = -1
        else:
            post.downvotes += 1; self._post_votes[user_id][post_id] = -1
        self._recalc_post_karma(post.author_id)
        self._refresh_post(post_id)
        return True

    def get_post_vote(self, post_id: int, user_id: int) -> int:
        return self._post_votes.get(user_id, {}).get(post_id, 0)

    def share_post(self, post_id: int, user_id: int) -> bool:
        post = self.posts.get(post_id)
        if not post or not self.users.exists(user_id):
            return False
        post.share_count += 1
        shares = self._post_shares.setdefault(user_id, {})
        shares[post_id] = shares.get(post_id, 0) + 1
        return True

    def get_post_share_count(self, post_id: int) -> int:
        post = self.posts.get(post_id)
        return post.share_count if post else 0

    # -------------------------------------------------------------------------
    # Comments
    # -------------------------------------------------------------------------

    def create_comment(self, author_id: int, post_id: int, content: str, parent_comment_id: Optional[int] = None) -> Optional[Comment]:
        if not self.users.exists(author_id):
            return None
        post = self.get_post(post_id)
        if not post:
            return None
        if parent_comment_id:
            parent = self.comments.get(parent_comment_id)
            if not parent or parent.post_id != post_id:
                return None
        now = datetime.now()
        comment = Comment(comment_id=self._next_comment_id, content=content, author_id=author_id, post_id=post_id, parent_comment_id=parent_comment_id, created_at=now, updated_at=now)
        self._next_comment_id += 1
        self.comments[comment.comment_id] = comment
        if post_id not in self._comment_trees:
            self._comment_trees[post_id] = CommentTree(-post_id)
        tree = self._comment_trees[post_id]
        tree.add_reply(parent_comment_id if parent_comment_id else -post_id, comment.comment_id)
        post.comments += 1
        for uid in self._post_votes:
            self._comment_votes.setdefault(uid, {}).setdefault(comment.comment_id, 0)
        return comment

    def get_comment(self, comment_id: int) -> Optional[Comment]:
        return self.comments.get(comment_id)

    def get_post_comments(self, post_id: int) -> List[Comment]:
        tree = self._comment_trees.get(post_id)
        if not tree:
            return []
        return [self.comments[cid] for cid in tree.get_all_comment_ids() if cid != post_id and cid in self.comments]

    def build_comment_thread(self, post_id: int, sort_by: str = "score") -> List[Dict]:
        tree = self._comment_trees.get(post_id)
        if not tree:
            return []
        return [self._build_subtree(cid, tree, sort_by) for cid in tree.children_of(-post_id)]

    def _build_subtree(self, comment_id: int, tree: CommentTree, sort_by: str) -> Dict:
        comment = self.comments.get(comment_id)
        if not comment:
            return {}
        author = self.get_user(comment.author_id)
        data = comment.to_dict()
        data["author_username"] = author.username if author and not comment.is_deleted else "[deleted]"
        _empty = Comment(0, "", 0, 0, None, datetime.now(), datetime.now())
        children = tree.children_of(comment_id)
        if sort_by == "score":
            children = sorted(children, key=lambda cid: self.comments.get(cid, _empty).score, reverse=True)
        else:
            children = sorted(children, key=lambda cid: self.comments.get(cid, _empty).created_at, reverse=True)
        data["children"] = [self._build_subtree(cid, tree, sort_by) for cid in children]
        return data

    def edit_comment(self, comment_id: int, content: str) -> bool:
        comment = self.comments.get(comment_id)
        if not comment or comment.is_deleted:
            return False
        comment.content = content
        comment.updated_at = datetime.now()
        comment.is_edited = True
        return True

    def delete_comment(self, comment_id: int) -> bool:
        comment = self.comments.get(comment_id)
        if not comment:
            return False
        tree = self._comment_trees.get(comment.post_id)
        if not tree:
            return False
        tree.delete_comment(comment_id)
        if tree.is_deleted(comment_id):
            comment.is_deleted = True
            comment.content = "[deleted]"
        else:
            del self.comments[comment_id]
        post = self.get_post(comment.post_id)
        if post:
            post.comments -= 1
        return True

    def get_comment_depth(self, post_id: int) -> int:
        tree = self._comment_trees.get(post_id)
        return (tree.max_depth() - 1) if tree else 0

    def get_user_comments(self, user_id: int) -> List[Comment]:
        return [c for c in self.comments.values() if c.author_id == user_id]

    # -------------------------------------------------------------------------
    # Comment votes
    # -------------------------------------------------------------------------

    def upvote_comment(self, comment_id: int, user_id: int) -> bool:
        comment = self.comments.get(comment_id)
        if not comment or not self.users.exists(user_id):
            return False
        votes = self._comment_votes.setdefault(user_id, {})
        current = votes.get(comment_id, 0)
        if current == 1:
            comment.upvotes -= 1; votes[comment_id] = 0
        elif current == -1:
            comment.downvotes -= 1; comment.upvotes += 1; votes[comment_id] = 1
        else:
            comment.upvotes += 1; votes[comment_id] = 1
        self._recalc_comment_karma(comment.author_id)
        return True

    def downvote_comment(self, comment_id: int, user_id: int) -> bool:
        comment = self.comments.get(comment_id)
        if not comment or not self.users.exists(user_id):
            return False
        votes = self._comment_votes.setdefault(user_id, {})
        current = votes.get(comment_id, 0)
        if current == -1:
            comment.downvotes -= 1; votes[comment_id] = 0
        elif current == 1:
            comment.upvotes -= 1; comment.downvotes += 1; votes[comment_id] = -1
        else:
            comment.downvotes += 1; votes[comment_id] = -1
        self._recalc_comment_karma(comment.author_id)
        return True

    def get_comment_vote(self, comment_id: int, user_id: int) -> int:
        return self._comment_votes.get(user_id, {}).get(comment_id, 0)

    # -------------------------------------------------------------------------
    # Recommendations
    # -------------------------------------------------------------------------

    def get_recommendations(self, user_id: int, limit: int = 10) -> List[SubredditRecommendation]:
        return self.recommendation_engine.recommend(user_id, limit)

    # -------------------------------------------------------------------------
    # Search
    # -------------------------------------------------------------------------

    def search_posts(self, query: str, limit: int) -> List[Post]:
        q = query.lower()
        return [p for p in self.posts.values() if q in p.title.lower() or q in p.content.lower()][:limit]

    def search_subreddits(self, query: str, limit: int) -> List[Subreddit]:
        q = query.lower()
        return [s for s in self.subreddits.values() if q in s.name.lower() or q in s.description.lower()][:limit]

    def search_users(self, query: str, limit: int) -> List[Redditor]:
        q = query.lower()
        return [u for u in self.users.get_all() if q in u.username.lower()][:limit]

    # -------------------------------------------------------------------------
    # Private helpers
    # -------------------------------------------------------------------------

    def _populate_feed(self, user_id: int, subreddit_id: int) -> None:
        feed = self._feeds.get(user_id)
        if feed:
            for pid in self._subreddit_posts.get(subreddit_id, []):
                post = self.posts.get(pid)
                if post:
                    feed.add_post(post)

    def _remove_feed_posts(self, user_id: int, subreddit_id: int) -> None:
        feed = self._feeds.get(user_id)
        if feed:
            for pid in self._subreddit_posts.get(subreddit_id, []):
                feed.remove_post(pid)

    def _refresh_post(self, post_id: int) -> None:
        post = self.posts.get(post_id)
        if not post:
            return
        for user_id, node in self.nodes.items():
            if node.is_subscribed(post.subreddit_id):
                feed = self._feeds.get(user_id)
                if feed and post_id in feed.post_ids:
                    feed.refresh_priorities(self.posts)

    def _recalc_post_karma(self, author_id: int) -> None:
        author = self.users.get_by_id(author_id)
        if author:
            author.post_karma = sum(self.posts[pid].score for pid in self._user_posts.get(author_id, []) if pid in self.posts)

    def _recalc_comment_karma(self, author_id: int) -> None:
        author = self.users.get_by_id(author_id)
        if author:
            author.comment_karma = sum(c.score for c in self.comments.values() if c.author_id == author_id)


# =============================================================================
# SINGLETON + SEED DATA
# =============================================================================

reddit_db = RedditSystem()


def load_dummy_data() -> None:
    if reddit_db.users.get_all():
        return

    seattle = Location(47.6062, -122.3321, "Seattle", "Washington", "USA")
    paris = Location(48.8566, 2.3522, "Paris", "Île-de-France", "France")
    nyc = Location(40.7128, -74.0060, "New York", "New York", "USA")

    subs_data = [
        ("algorithms", "Graph theory, complexity, raw implementations.", None, "computer science"),
        ("python", "Python news, tips and projects.", None, "programming"),
        ("webdev", "Frontend, backend, devops.", None, "web development"),
        ("geothread", "GeoThread project discussion.", LocationScope("city", paris, 50), "project"),
        ("ParisTech", "Paris software, startups, and engineering meetups.", LocationScope("city", paris, 50), "local tech"),
        ("Seattle", "Everything Seattle", LocationScope("city", seattle, 50), "local"),
        ("SeattleFood", "Best eats in Seattle", LocationScope("city", seattle, 50), "food"),
        ("Paris", "Paris community", LocationScope("city", paris, 50), "local"),
        ("NYC", "New York City", LocationScope("city", nyc, 50), "local"),
        ("PacificNorthwest", "WA, OR, BC", LocationScope("region", seattle), "regional"),
        ("programming", "Programming discussion", None, "programming"),
        ("technology", "Tech news", None, "technology"),
    ]
    subreddits = [reddit_db.create_subreddit(name, desc, scope, topic) for name, desc, scope, topic in subs_data]

    users_data = [
        ("helmi_dev", "helmi@geo.io", "hot", Location(48.8566, 2.3522, "Paris", "Île-de-France", "France")),
        ("sara_algo", "sara@geo.io", "new", Location(48.8584, 2.2945, "Paris", "Île-de-France", "France")),
        ("pedro_graphs", "pedro@geo.io", "top", Location(48.8534, 2.3332, "Paris", "Île-de-France", "France")),
        ("nour_isep", "nour@geo.io", "controversial", Location(48.8924, 2.2381, "Paris", "Île-de-France", "France")),
        ("alex_cs", "alex@geo.io", "hot", nyc),
        ("maya_fullstack", "maya@geo.io", "rising", seattle),
    ]
    users = [reddit_db.create_user(u, e, sort=s, location=loc) for u, e, s, loc in users_data]

    for user in users:
        for subreddit in subreddits[:4]:
            reddit_db.subscribe(user.user_id, subreddit.subreddit_id)
    reddit_db.subscribe(users[0].user_id, subreddits[7].subreddit_id)
    reddit_db.subscribe(users[5].user_id, subreddits[9].subreddit_id)

    now = datetime.now()
    posts_data = [
        (users[0], subreddits[0], "Why Dijkstra fails on negative weights — and what to use instead",
         "Dijkstra breaks with negative edges because the greedy relaxation assumes finalized distances cannot improve. Bellman-Ford is the straightforward alternative.", 45, 3420, 180, 48.8584, 2.2945),
        (users[1], subreddits[1], "I built a Reddit clone backend in pure Python — no graph libraries",
         "For my algorithms class I implemented graph traversal, nested comments, feed ranking, voting, and geospatial recommendations from scratch.", 180, 1850, 95, 48.8867, 2.3431),
        (users[2], subreddits[2], "Tailwind v4 is actually great — here is what changed",
         "The new Vite integration is clean, CSS-first config works well, and the upgrade path is much smaller than I expected.", 720, 920, 310, 48.8534, 2.3332),
        (users[0], subreddits[3], "GeoThread ASNAP engine — first working demo",
         "Feed sorting with hot/new/top/rising/controversial is live. Comment tree traversal and location-aware community recommendations are connected.", 10, 8, 1, 48.8574, 2.3578),
        (users[3], subreddits[0], "Union-Find vs label propagation for community detection — which is better?",
         "Union-Find is simpler and near-constant amortized. Label propagation produces richer clusters but is harder to tune.", 2160, 610, 580, 48.8924, 2.2381),
        (users[4], subreddits[10], "Recursion vs iteration — when does it actually matter?",
         "Stack overflow is the obvious risk, but the real tradeoff is readability, state ownership, and control over memory.", 120, 2100, 140, 40.7128, -74.0060),
        (users[5], subreddits[2], "React Server Components finally make sense to me",
         "The useful mental model is two component trees with a serialization boundary, not one magic tree that runs everywhere.", 300, 1430, 210, 47.6062, -122.3321),
        (users[1], subreddits[1], "Python 3.14 is faster than ever — here are the benchmarks",
         "The latest interpreter work is producing real speedups across CPU-heavy workloads and web services.", 480, 4800, 90, 48.8049, 2.1204),
        (users[2], subreddits[0], "Implementing a min-heap from scratch in 30 lines of Python",
         "Raw list manipulation is a useful way to understand the invariant before reaching for heapq.", 1200, 780, 45, 48.8396, 2.2456),
        (users[4], subreddits[10], "The two-sum problem has an O(n) solution — most people miss it",
         "A one-pass hash map stores complements as you scan. The implementation is shorter and easier to reason about.", 1440, 3200, 120, None, None),
        (users[5], subreddits[4], "Best coffee near Pike Place right now?",
         "I am visiting Seattle this weekend and want something better than the obvious tourist stops.", 75, 120, 8, 47.6097, -122.3425),
        (users[1], subreddits[7], "Meilleurs endroits à Paris pour coder",
         "Partagez vos cafés, bibliothèques, et spots calmes pour travailler sur des projets.", 95, 340, 22, 48.8462, 2.3449),
    ]

    posts = []
    for author, subreddit, title, content, minutes_ago, upvotes, downvotes, latitude, longitude in posts_data:
        post = reddit_db.create_post(author.user_id, subreddit.subreddit_id, title, content, latitude, longitude)
        if not post:
            continue
        post.timestamp = now - timedelta(minutes=minutes_ago)
        post.upvotes = upvotes
        post.downvotes = downvotes
        posts.append(post)

    comments_data = [
        (posts[0], users[1], None, "Great explanation. The key insight is the greedy relaxation assumption."),
        (posts[0], users[2], 1, "Exactly. Bellman-Ford runs in O(VE), which matters at scale."),
        (posts[0], users[4], 2, "Worth noting: Bellman-Ford also detects negative cycles."),
        (posts[0], users[3], None, "What about A*? Is it also broken on negative weights?"),
        (posts[0], users[0], 4, "Yes. A* has the same issue when the priority can be invalidated by negative edges."),
        (posts[3], users[1], None, "The API is much easier to demo now that every feature has a visible UI path."),
        (posts[3], users[5], 6, "The location recommendations are the strongest GeoThread-specific piece."),
        (posts[11], users[0], None, "Bibliothèque Sainte-Geneviève is hard to beat if you can get a seat."),
    ]
    for post, author, parent_id, content in comments_data:
        comment = reddit_db.create_comment(author.user_id, post.post_id, content, parent_id)
        if comment:
            comment.upvotes = 10
            comment.downvotes = 1

    for user in users:
        for post in posts[:6]:
            if user.user_id != post.author_id:
                reddit_db.upvote_post(post.post_id, user.user_id)

    for user in users:
        reddit_db._recalc_post_karma(user.user_id)
        reddit_db._recalc_comment_karma(user.user_id)
