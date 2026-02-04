# AI Operations Assistant

A multi-agent AI assistant that accepts natural-language tasks, plans steps, calls tools (APIs), and returns structured answers.

## Architecture

```
User Request → Planner Agent → Executor Agent → Verifier Agent → Final Response
                    ↓               ↓
              (LLM Planning)   (GitHub API, Weather API)
```

### Agents

| Agent | Role |
|-------|------|
| **Planner** | Uses LLM to create step-by-step execution plan |
| **Executor** | Calls tools/APIs with retry logic |
| **Verifier** | Validates results and formats final output |

### Tools

| Tool | API | Actions |
|------|-----|---------|
| GitHub | api.github.com | `search_repos`, `get_repo`, `get_user`, `get_repo_languages` |
| Weather | api.openweathermap.org | `get_current`, `get_forecast` |

## Quick Start

### 1. Install Dependencies

```bash
cd ai_ops_assistant
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

Required keys:
- `GEMINI_API_KEY` - Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- `OPENWEATHERMAP_API_KEY` - Get from [OpenWeatherMap](https://openweathermap.org/api)

### 3. Run the Server

```bash
uvicorn main:app --reload
```

Server runs at: http://localhost:8000

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| GET | `/tools` | List available tools |
| POST | `/query` | Submit a task |

### Example Request

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"task": "Search for popular Python repos and get weather in London"}'
```

### Example Response

```json
{
  "task": "Search for popular Python repos...",
  "status": "success",
  "stages": {
    "planning": {"status": "success", "steps": [...]},
    "execution": {"status": "success", "results": [...]},
    "verification": {"status": "success", "is_complete": true}
  },
  "final_answer": "Here are the top Python repositories...",
  "summary": "Successfully retrieved data from GitHub and Weather APIs."
}
```

## Project Structure

```
ai_ops_assistant/
├── agents/
│   ├── planner.py      # Creates execution plans
│   ├── executor.py     # Executes tools
│   ├── verifier.py     # Validates results
│   └── orchestrator.py # Coordinates workflow
├── tools/
│   ├── base.py         # Tool interface
│   ├── github_tool.py  # GitHub API
│   └── weather_tool.py # Weather API
├── llm/
│   └── client.py       # Gemini LLM client
├── main.py             # FastAPI app
├── requirements.txt
├── .env.example
└── README.md
```

## Requirements Met

-  Multi-agent design (Planner, Executor, Verifier)
-  LLM with structured outputs (Gemini API)
-  2+ real third-party APIs (GitHub + OpenWeatherMap)
-  End-to-end result
-  No hardcoded responses
- Single command run: `uvicorn main:app`

