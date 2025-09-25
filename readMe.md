# GitHub Repository Scorer

A FastAPI application that fetches GitHub repositories for a given programming language and creation date, calculates a **popularity score** for each repository, and returns a paginated, sorted list via a REST API.  


## Features

- Fetch repositories from GitHub using the official REST API
- Compute a popularity score for each repository based on -
  - Stars
  - Forks
  - Recency of last push
- Sort repositories by popularity and other metrics
- Configurable parameters -
  - Programming language (`language`)
  - Earliest creation date (`created_after`)
  - Pagination (`page` and `per_page`)
- In-memory caching to reduce API calls and improve performance
- Fully tested, with both unit tests and integration tests


## Popularity Scoring

The popularity score is calculated as -  

```
popularity_score = stars + 0.5 * forks + recency_score
```
Where `recency_score` is higher for recently pushed repositories -

```
recency_score = 100 / (1 + days_since_push)
```


## API Endpoint

### GET `/repositories`

**Query Parameters**

|Parameter|Type|Default|Description
|--|--|--|--|
|language|string|Python|Programming language|
|created_after|string|today’s date|Filter repos created after this date (YYYY-MM-DD)|
|per_page|int|20|Number of repositories per page (max 100)|
|page|int|1|Page number (>= 1)|

**Response Model: List of repositories with**
```
{
  "full_name": "username/repo",
  "html_url": "https://github.com/username/repo",
  "description": "Repo description",
  "stargazers_count": 123,
  "forks_count": 45,
  "pushed_at": "2025-09-23T09:04:09Z",
  "popularity_score": 154.69
}
```


## Installation

### Requirements -
1. Python 3.11+
2. pip

```
# Clone the repo
git clone <repo-url>
cd github_scoring

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Dependencies:

1. fastapi – web framework

2. httpx – async HTTP client

3. pytest – testing framework

4. respx – HTTPX mocking for tests


## Running the Application
Inside tge virtual environment, run -
```
uvicorn app.main:app --reload
```

**Example Request**
```
GET http://127.0.0.1:8000/repositories?language=Python&created_after=2025-01-01&page=6&per_page=50
```

**Example Response**
```
[
  {
    "full_name": "Wirasm/PRPs-agentic-eng",
    "html_url": "https://github.com/Wirasm/PRPs-agentic-eng",
    "description": "Prompts, workflows and more for agentic engineering ",
    "stargazers_count": 1547,
    "forks_count": 496,
    "pushed_at": "2025-08-27T07:49:41Z",
    "popularity_score": 1798.57
  },
  {
    "full_name": "gensyn-ai/rl-swarm",
    "html_url": "https://github.com/gensyn-ai/rl-swarm",
    "description": "A fully open source framework for creating RL training swarms over the internet.",
    "stargazers_count": 1428,
    "forks_count": 541,
    "pushed_at": "2025-08-27T15:02:43Z",
    "popularity_score": 1702.2
  },
  {
    "full_name": "disler/claude-code-hooks-mastery",
    "html_url": "https://github.com/disler/claude-code-hooks-mastery",
    "description": null,
    "stargazers_count": 1513,
    "forks_count": 347,
    "pushed_at": "2025-08-21T16:32:47Z",
    "popularity_score": 1689.53
  },
  {
    "full_name": "ravendevteam/talon",
    "html_url": "https://github.com/ravendevteam/talon",
    "description": "Simple utility to debloat Windows in 2 clicks.",
    "stargazers_count": 1536,
    "forks_count": 62,
    "pushed_at": "2025-09-23T02:10:09Z",
    "popularity_score": 1667
  },
  {
    "full_name": "NVIDIA/NeMo-Agent-Toolkit",
    "html_url": "https://github.com/NVIDIA/NeMo-Agent-Toolkit",
    "description": "The NVIDIA NeMo Agent toolkit is an open-source library for efficiently connecting and optimizing teams of AI agents.",
    "stargazers_count": 1374,
    "forks_count": 368,
    "pushed_at": "2025-09-23T04:41:05Z",
    "popularity_score": 1658
  },
  {
    "full_name": "guy-hartstein/company-research-agent",
    "html_url": "https://github.com/guy-hartstein/company-research-agent",
    "description": "An agentic company research tool powered by LangGraph and Tavily that conducts deep diligence on companies using a multi-agent framework. It leverages Google's Gemini 2.5 Flash and OpenAI's GPT-4.1 on the backend for inference.",
    "stargazers_count": 1444,
    "forks_count": 215,
    "pushed_at": "2025-09-22T16:01:42Z",
    "popularity_score": 1651.5
  },

  ...

  ...
```


## Caching
1. In-memory caching is implemented with a simple dictionary
2. Cache key: (language, created_after, per_page, page)
3. Cache TTL (time-to-live): 10 minutes (CACHE_TTL = 600)
4. Reduces redundant GitHub API calls


## Unit Testing
Run tests using pytest. Install the dependencies in the virtual environment which would be running from above -
```
pip install pytest pytest-asyncio respx httpx
```
```
pytest tests/ -v
```

## Scalability
The application entertains the following aspects in terms of scalability -
1. **Separation of Concerns** The code is modular allowing each component to scale independently. For example, you can update the scoring logic or API client without affecting the FastAPI app.
2. **Asynchronous I/O** HTTPX is used for asynchronous I/O for API requests. Using async/await allows multiple requests to GitHub to be made concurrently, threby improving throughput and reducing the latency compared to sync calls.
3. **Pagination Support** The API endpoint supports page and page-size parameters allowing the data to be fetched in chunks.

## Some Nice to Knows 
1. GitHub API rate limits is applicable for unauthenticated requests. Using a personal access token increases this limit. This can be easily done by setting the access token as environment variable as one of the options -
```
import os

HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"

```
2. Popularity score is rounded to 2 decimal places
3. For repositories with the same popularity score, sorting is based on -
 - Stars
 - Forks
 - Last pushed timestamp
4. **Important limitation** The GitHub Search API only returns the first 1,000 results per query. That means -
 - per_page can be at most 100
 - page can be at most 10 when per_page=100
 - Requests beyond this (for example, page=11&per_page=100) will return **HTTP 422 Unprocessable Entity**
GitHub does this to keep search performant and to discourage full-dataset crawling. This also means that -
 - Your popularity score is only computed for the repositories returned by GitHub
 - Repositories beyond the 1000th result (for a given query) are never fetched and therefore never scored
 - As a result, the ranking is not guaranteed to include every GitHub repository, only the top repositories within the API’s first 1,000 results

**To handle** this, one can split the query into smaller buckets such as date ranges (created:2025-08-01..2025-08-31). But the key idea would be to reduce each individual query so that it always returns fewer than 1000 results, then fetch all of those smaller result sets and combine them. It is difficult to predict the date range that returns less than 1000 results in the API response. Even the date range of 1 day (for exmaple: 2024-09-01..2024-09-02) gives more than 1000 results.
