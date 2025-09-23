from pydantic import BaseModel
from typing import Optional

class Repository(BaseModel):
    full_name: str
    html_url: str
    description: Optional[str] = None
    stargazers_count: int
    forks_count: int
    pushed_at: str
    popularity_score: float

