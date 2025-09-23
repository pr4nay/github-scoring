import pytest
import respx
from httpx import Response, HTTPStatusError
from app.github_client import fetch_repositories, _cache, CACHE_TTL
import time

SAMPLE_REPOS = [
    {"full_name": "user/repo1", "stargazers_count": 10, "forks_count": 5, "pushed_at": "2025-01-01T00:00:00Z"},
    {"full_name": "user/repo2", "stargazers_count": 20, "forks_count": 2, "pushed_at": "2025-01-02T00:00:00Z"},
]

API_URL = "https://api.github.com/search/repositories"

@respx.mock
@pytest.mark.asyncio
async def test_fetch_repositories_cache_hit():
    respx.get(API_URL).mock(return_value=Response(200, json={"items": [{"full_name": "test/repo"}]}))

    # First call is cache MISS
    data1 = await fetch_repositories("Python", "2025-01-01", 10, 1)
    assert data1[0]["full_name"] == "test/repo"

    # Second call should be cache HIT
    start = time.time()
    data2 = await fetch_repositories("Python", "2025-01-01", 10, 1)
    end = time.time()
    assert data2[0]["full_name"] == "test/repo"

    assert end - start < 100

@respx.mock
@pytest.mark.asyncio
async def test_fetch_repositories_cache_expired():
    _cache.clear()
    key = ("Python", "2025-01-01", 10, 1)
    _cache[key] = (time.time() - CACHE_TTL - 100, SAMPLE_REPOS)

    route = respx.get(API_URL).mock(return_value=Response(200, json={"items": SAMPLE_REPOS}))
    data = await fetch_repositories("Python", "2025-01-01", 10, 1)

    assert route.called
    assert data == SAMPLE_REPOS       

@respx.mock
@pytest.mark.asyncio
async def test_fetch_repositories_pagination():
    _cache.clear()
    route1 = respx.get(API_URL).mock(return_value=Response(200, json={"items": SAMPLE_REPOS[0]}))
    repo1_data = await fetch_repositories("Python", "2025-01-01", per_page=1, page=1)
    assert route1.called
    assert repo1_data["full_name"] == SAMPLE_REPOS[0]["full_name"]

    route2 = respx.get(API_URL).mock(return_value=Response(200, json={"items": SAMPLE_REPOS[1]}))
    repo2_data = await fetch_repositories("Python", "2025-01-01", per_page=1, page=2)
    assert route2.called
    assert repo2_data["full_name"] == SAMPLE_REPOS[1]["full_name"]

@respx.mock
@pytest.mark.asyncio
async def test_fetch_repositories_empty_response():
    route = respx.get(API_URL).mock(return_value=Response(200, json={"items": []}))
    
    data = await fetch_repositories("Python", "2025-01-01", per_page=10, page=1)
    
    assert route.called
    assert data == []

