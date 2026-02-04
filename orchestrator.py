from typing import Any
from llm.client import LLMClient
from tools.base import ToolRegistry
from .planner import PlannerAgent
from .executor import ExecutorAgent
from .verifier import VerifierAgent


class Orchestrator:
    
    def __init__(self, llm_client: LLMClient, tool_registry: ToolRegistry):
        self.llm = llm_client
        self.tools = tool_registry
        self.planner = PlannerAgent(llm_client, tool_registry)
        self.executor = ExecutorAgent(tool_registry)
        self.verifier = VerifierAgent(llm_client)
    
    async def process_task(self, task: str) -> dict[str, Any]:
        response = {"task": task, "stages": {}}
        
        try:
            plan = await self.planner.create_plan(task)
            response["stages"]["planning"] = {
                "status": "success",
                "task_understanding": plan.get("task_understanding"),
                "steps": plan.get("steps")
            }
            
            execution_result = await self.executor.execute_plan(plan)
            response["stages"]["execution"] = {
                "status": "success",
                "results": execution_result.get("results")
            }
            
            final_result = await self.verifier.verify_and_format(execution_result)
            response["stages"]["verification"] = {
                "status": "success",
                "is_complete": final_result.get("is_complete"),
                "missing_information": final_result.get("missing_information")
            }
            
            response["final_answer"] = final_result.get("final_answer")
            response["summary"] = final_result.get("summary")
            response["status"] = "success"
            
        except Exception as e:
            response["status"] = "error"
            response["error"] = str(e)
        
        return response
