from typing import Any
from llm.client import LLMClient


class VerifierAgent:
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
    
    async def verify_and_format(self, execution_result: dict[str, Any]) -> dict[str, Any]:
        original_task = execution_result.get("original_task", "")
        plan = execution_result.get("plan", {})
        results = execution_result.get("results", [])
        
        errors = [r for r in results if r.get("status") == "error"]
        successful = [r for r in results if r.get("status") == "success"]
        
        verification = await self.llm.verify_results(original_task, plan, results)
        
        return {
            "original_task": original_task,
            "plan_summary": plan.get("task_understanding", ""),
            "steps_executed": len(results),
            "steps_successful": len(successful),
            "steps_failed": len(errors),
            "is_complete": verification.get("is_complete", False),
            "missing_information": verification.get("missing_information", []),
            "final_answer": verification.get("final_answer", ""),
            "summary": verification.get("summary", ""),
            "detailed_results": results
        }
