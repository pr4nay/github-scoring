from app.models import Repository
import pytest

def test_repository_model_validation():
    repo_data = {
        "full_name": "test/repo",
        "html_url": "https://github.com/test/repo",
        "description": "desc",
        "stargazers_count": 10,
        "forks_count": 5,
        "pushed_at": "2025-01-01T00:00:00Z",
        "popularity_score": 123.45
    }
    repo = Repository(**repo_data)
    assert repo.full_name == "test/repo"
    assert repo.popularity_score == 123.45

def test_repository_model_missing_optional():
    repo_data = {
        "full_name": "test/repo",
        "html_url": "https://github.com/test/repo",
        "stargazers_count": 0,
        "forks_count": 0,
        "pushed_at": "2025-01-01T00:00:00Z",
        "popularity_score": 0
    }
    repo = Repository(**repo_data)
    assert repo.description is None
