# Comment Analysis

Analyze and categorize YouTube comments with an asynchronous FastAPI service powered by AI. Submit a YouTube video URL, receive a task ID immediately, and poll Redis-backed task status until the categorized comments are ready.

## Tech stack

![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.162%2B-009688?logo=fastapi&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-2.x-E92063?logo=pydantic&logoColor=white)
![Pydantic AI](https://img.shields.io/badge/Pydantic_AI-2.x-E92063)
![Redis](https://img.shields.io/badge/Redis-8.x-DC382D?logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![uv](https://img.shields.io/badge/uv-package_manager-6C47FF)
![OpenAI](https://img.shields.io/badge/OpenAI-o3--mini-412991?logo=openai&logoColor=white)

## How it works

1. The client sends a YouTube URL to `POST /analyze`.
2. The API creates a task ID and schedules comment processing in the background.
3. The worker fetches top-level comments through the YouTube Data API.
4. Pydantic AI classifies each comment with OpenAI's `o3-mini` model.
5. The result is stored in Redis and can be retrieved through `GET /status/{task_id}`.

Comments are classified into:

- Video suggestion
- Questions
- Thanks
- Advice/tips
- Corrections
- Summaries
- Bots
- Feedback

## Project structure

```text
.
├── backend/
│   ├── main.py          # FastAPI app and analysis workflow
│   ├── models.py        # Settings and request/response models
│   ├── prompts.py       # Comment classification prompt
│   ├── pyproject.toml   # Python dependencies and project metadata
│   └── uv.lock          # Locked dependency versions
└── docker-compose.yml   # Local Redis service
```

## Prerequisites

- Python 3.12 or newer
- [uv](https://docs.astral.sh/uv/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (for Redis)
- A YouTube Data API v3 key
- An OpenAI API key

## Quick start

### 1. Start Redis

From the repository root:

```bash
docker compose up -d redis
```

### 2. Configure the backend

Create `backend/.env`:

```env
FRONTEND_URL=http://localhost:3000
REDIS_URL=redis://localhost:6379
YOUTUBE_API_KEY=your_youtube_api_key
OPENAI_API_KEY=your_openai_api_key
```

Never commit `.env` files or API keys to version control.

### 3. Install dependencies

```bash
cd backend
uv sync
```

### 4. Run the API

```bash
uv run fastapi dev main.py --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`. Interactive OpenAPI documentation is available at [`http://localhost:8000/docs`](http://localhost:8000/docs).

## API reference

### Start an analysis

```http
POST /analyze
Content-Type: application/json
```

Request:

```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

Response:

```json
{
  "task_id": "generated-task-uuid"
}
```

### Check task status

```http
GET /status/{task_id}
```

Example response while processing:

```json
{
  "task_id": "generated-task-uuid",
  "status": "processing",
  "data": {}
}
```

Example completed response:

```json
{
  "task_id": "generated-task-uuid",
  "status": "completed",
  "data": {
    "Questions": [
      {
        "id": "comment-id",
        "text": "How did you build this?"
      }
    ]
  }
}
```

## Development

Run the API from the `backend` directory so local imports and `.env` loading work as expected:

```bash
cd backend
uv run fastapi dev main.py
```

Useful checks:

```bash
cd backend
uv lock --check
uv run python -m compileall main.py models.py prompts.py
```

Stop the local Redis service when finished:

```bash
docker compose down
```

## Current limitations

- The service currently processes top-level comments returned by the YouTube API.
- A YouTube URL must contain a `v` query parameter.
- Analysis runs in FastAPI background tasks; Redis stores the task state and result.
- The frontend is not implemented in this repository yet.
- The default AI model is `openai:o3-mini`; configure access through `OPENAI_API_KEY`.

## License

No license has been specified yet.
