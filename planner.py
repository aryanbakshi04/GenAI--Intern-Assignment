from typing import Any
from llm.client import LLMClient
from tools.base import ToolRegistry


class PlannerAgent:
    
    def __init__(self, llm_client: LLMClient, tool_registry: ToolRegistry):
        self.llm = llm_client
        self.tools = tool_registry
    
    async def create_plan(self, task: str) -> dict[str, Any]:
        available_tools = self.tools.list_tools()
        plan = await self.llm.generate_plan(task, available_tools)
        validated_plan = self._validate_plan(plan)
        
        return {
            "original_task": task,
            "task_understanding": validated_plan.get("task_understanding", ""),
            "steps": validated_plan.get("steps", []),
            "status": "created"
        }
    
    def _validate_plan(self, plan: dict) -> dict:
        validated_steps = []
        
        for step in plan.get("steps", []):
            tool_name = step.get("tool", "")
            
            if self.tools.get(tool_name):
                validated_steps.append({
                    "step_number": step.get("step_number", len(validated_steps) + 1),
                    "description": step.get("description", ""),
                    "tool": tool_name,
                    "action": step.get("action", ""),
                    "parameters": step.get("parameters", {})
                })
        
        return {
            "task_understanding": plan.get("task_understanding", ""),
            "steps": validated_steps
        }
