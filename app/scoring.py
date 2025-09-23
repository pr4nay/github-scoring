from datetime import datetime, timezone

def calculate_popularity(repo: dict) -> float:
    stars = repo.get("stargazers_count", 0)
    forks = repo.get("forks_count", 0)
    pushed_at = repo.get("pushed_at")

    recency = 1.0
    if pushed_at:
        dt = datetime.fromisoformat(pushed_at)
        now = datetime.now(timezone.utc)
        days_since_push = (now - dt).days
        recency = 1 / (1 + days_since_push)

    return round(stars + forks * 0.5 + recency * 100, 2)

