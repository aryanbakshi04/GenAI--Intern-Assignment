from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from llm.client import LLMClient
from tools.base import ToolRegistry
from tools.github_tool import GitHubTool
from tools.weather_tool import WeatherTool
from agents.orchestrator import Orchestrator

load_dotenv()


class TaskRequest(BaseModel):
    task: str
    
    class Config:
        json_schema_extra = {
            "example": {"task": "Find popular Python machine learning repos on GitHub and get the weather in San Francisco"}
        }


class TaskResponse(BaseModel):
    task: str
    status: str
    stages: dict
    final_answer: str | None = None
    summary: str | None = None
    error: str | None = None


tool_registry: ToolRegistry | None = None
orchestrator: Orchestrator | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global tool_registry, orchestrator
    
    llm_client = LLMClient()
    tool_registry = ToolRegistry()
    
    github_tool = GitHubTool()
    weather_tool = WeatherTool()
    
    tool_registry.register(github_tool)
    tool_registry.register(weather_tool)
    
    orchestrator = Orchestrator(llm_client, tool_registry)
    
    yield
    
    await github_tool.close()
    await weather_tool.close()


app = FastAPI(
    title="AI Operations Assistant",
    description="Multi-agent AI assistant with Planner, Executor, and Verifier agents",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "name": "AI Operations Assistant",
        "version": "1.0.0",
        "description": "Multi-agent AI assistant for natural language task processing",
        "endpoints": {
            "POST /query": "Submit a natural language task",
            "GET /tools": "List available tools",
            "GET /health": "Health check"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/tools")
async def list_tools():
    if tool_registry is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    return {"tools": tool_registry.list_tools()}


@app.post("/query", response_model=TaskResponse)
async def process_query(request: TaskRequest):
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    if not request.task.strip():
        raise HTTPException(status_code=400, detail="Task cannot be empty")
    
    result = await orchestrator.process_task(request.task)
    
    return TaskResponse(
        task=result.get("task", request.task),
        status=result.get("status", "unknown"),
        stages=result.get("stages", {}),
        final_answer=result.get("final_answer"),
        summary=result.get("summary"),
        error=result.get("error")
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
