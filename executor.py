import asyncio
from typing import Any
from tools.base import ToolRegistry


class ExecutorAgent:
    
    def __init__(self, tool_registry: ToolRegistry):
        self.tools = tool_registry
        self.max_retries = 2
        self.retry_delay = 1.0
    
    async def execute_plan(self, plan: dict[str, Any]) -> dict[str, Any]:
        results = []
        
        for step in plan.get("steps", []):
            step_result = await self._execute_step(step)
            results.append(step_result)
            
            status = step_result.get("status", "unknown")
            step_num = step_result.get("step_number", "?")
            print(f"[Executor] Step {step_num}: {status}")
        
        return {
            "original_task": plan.get("original_task", ""),
            "plan": plan,
            "results": results,
            "status": "executed",
            "summary": self._generate_summary(results)
        }
    
    async def _execute_step(self, step: dict) -> dict[str, Any]:
        tool_name = step.get("tool", "")
        action = step.get("action", "")
        parameters = step.get("parameters", {})
        step_number = step.get("step_number", 0)
        description = step.get("description", "")
        
        tool = self.tools.get(tool_name)
        
        if not tool:
            return {
                "step_number": step_number,
                "description": description,
                "tool": tool_name,
                "action": action,
                "status": "error",
                "error": f"Tool '{tool_name}' not found",
                "data": None
            }
        
        if action not in tool.actions:
            return {
                "step_number": step_number,
                "description": description,
                "tool": tool_name,
                "action": action,
                "status": "error",
                "error": f"Action '{action}' not supported by tool '{tool_name}'. Available: {tool.actions}",
                "data": None
            }
        
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                result = await tool.execute(action, parameters)
                
                if "error" not in result:
                    return {
                        "step_number": step_number,
                        "description": description,
                        "tool": tool_name,
                        "action": action,
                        "parameters": parameters,
                        "status": "success",
                        "data": result,
                        "attempts": attempt + 1
                    }
                else:
                    last_error = result.get("error")
                    if attempt < self.max_retries:
                        await asyncio.sleep(self.retry_delay)
                        
            except Exception as e:
                last_error = str(e)
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay)
        
        return {
            "step_number": step_number,
            "description": description,
            "tool": tool_name,
            "action": action,
            "parameters": parameters,
            "status": "error",
            "error": last_error,
            "data": None,
            "attempts": self.max_retries + 1
        }
    
    def _generate_summary(self, results: list[dict]) -> dict[str, Any]:
        successful = [r for r in results if r.get("status") == "success"]
        failed = [r for r in results if r.get("status") == "error"]
        
        return {
            "total_steps": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful) / len(results) if results else 0,
            "failed_steps": [
                {"step": r.get("step_number"), "error": r.get("error")}
                for r in failed
            ]
        }
