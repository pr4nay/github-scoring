import pytest
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch
from app.main import app

SAMPLE_REPOS = [
    {
        "full_name": "user/repo1",
        "html_url": "https://github.com/user/repo1",
        "description": "Test repo 1",
        "stargazers_count": 10,
        "forks_count": 5,
        "pushed_at": "2025-01-01T00:00:00Z"
    },
    {
        "full_name": "user/repo2",
        "html_url": "https://github.com/user/repo2",
        "description": "Test repo 2",
        "stargazers_count": 20,
        "forks_count": 2,
        "pushed_at": "2025-01-02T00:00:00Z"
    },
]

@pytest.mark.asyncio
async def test_get_repositories_endpoint():
    with patch("app.main.fetch_repositories", return_value=SAMPLE_REPOS):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/repositories?language=Python&created_after=2025-01-01&page=2&per_page=10")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(SAMPLE_REPOS)
    for repo, sample in zip(data, SAMPLE_REPOS):
        assert repo["full_name"] == sample["full_name"]
        assert "popularity_score" in repo
