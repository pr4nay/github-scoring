from datetime import datetime, timezone, timedelta
from app.scoring import calculate_popularity

def make_repo(stars=0, forks=0, pushed_days_ago=None):
    """
    Helper to create repo dict with optional pushed_at date
    """
    pushed_at = None
    if pushed_days_ago is not None:
        dt = datetime.now(timezone.utc) - timedelta(days=pushed_days_ago)
        pushed_at = dt.isoformat()
    return {
        "stargazers_count": stars,
        "forks_count": forks,
        "pushed_at": pushed_at
    }

def test_calculate_popularity_zero_values():
    repo = make_repo()
    score = calculate_popularity(repo)
    assert score == 100

def test_calculate_popularity_recent_repo():
    repo = make_repo(stars=10, forks=5, pushed_days_ago=1)
    score = calculate_popularity(repo)
    assert score > 10

def test_calculate_popularity_only_forks():
    repo = make_repo(stars=0, forks=10, pushed_days_ago=10)
    score = calculate_popularity(repo)
    assert score > 5    


def test_calculate_popularity_recent_and_old():
    now = datetime.now(timezone.utc)
    recent_repo = make_repo(stars=10, forks=5, pushed_days_ago=0)
    old_repo = make_repo(stars=10, forks=5, pushed_days_ago=1)

    recent_score = calculate_popularity(recent_repo)
    old_score = calculate_popularity(old_repo)

    assert recent_score > old_score

