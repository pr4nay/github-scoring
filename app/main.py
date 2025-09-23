from datetime import datetime, date
from fastapi import FastAPI, Query, HTTPException
from operator import itemgetter
from typing import List
from app.github_client import fetch_repositories
from app.scoring import calculate_popularity
from app.models import Repository

app = FastAPI(title="GitHub Repository Scorer", version="1.0")

@app.get("/repositories", response_model=List[Repository])
async def get_repositories(
    language: str = Query("Python", description="Programming language"),                            # default language: Python
    created_after: str = Query(str(date.today()), description="Earliest created date YYYY-MM-DD"),  # default craeted after date: today
    per_page: int = Query(20, description="Repositories per page"),
    page: int = Query(1, description="Page number")
):
    if page < 1:
        raise HTTPException(status_code=400, detail="page must be >= 1")
    if per_page > 100:
        raise HTTPException(status_code=400, detail="per_page cannot exceed 100")

    repos = await fetch_repositories(language, created_after, per_page, page)
    if not repos:
        return []

    for repo in repos:
        repo["popularity_score"] = calculate_popularity(repo)

    repos.sort(
        key=lambda x: (
            x["popularity_score"],
            x["stargazers_count"],
            x["forks_count"],
            datetime.fromisoformat(x["pushed_at"].replace("Z", "+00:00"))
        ),
        reverse=True
    )

    return repos

