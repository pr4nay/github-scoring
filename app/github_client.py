import httpx
import logging
import time
from typing import List, Dict, Tuple
from app.constants import GITHUB_API_URL, HEADERS, CACHE_TTL

# Simple in-memory cache
_cache: dict[Tuple[str, str, int, int], Tuple[float, List[Dict]]] = {}

#Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

async def fetch_repositories(language: str, created_after: str, per_page: int = 10, page: int = 1) -> List[Dict]:
    """
    Fetch repositories from GitHub API with caching
    """
    key = (language, created_after, per_page, page)
    now = time.time()

    #If cache HIT
    if key in _cache:
        cached_time, cached_value = _cache[key]
        if now - cached_time < CACHE_TTL:
            logger.info(f"Cache HIT: {key}")
            return cached_value
        else:
            logger.info(f"Cache EXPIRED: {key}")

    # Else, cache MISS
    logger.info(f"Cache MISS: {key}")
    params = {
        "q": f"language:{language} created:>{created_after}",
        "sort": "stars",
        "order": "desc",
        "per_page": per_page,
        "page": page
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(GITHUB_API_URL, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json().get("items", [])

    # Store in cache
    _cache[key] = (now, data)

    return data

