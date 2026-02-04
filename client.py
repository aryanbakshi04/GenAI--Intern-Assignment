import os
import json
from typing import Any
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()


class LLMClient:
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")
    
    async def generate_structured(self, prompt: str, response_schema: dict[str, Any]) -> dict[str, Any]:
        schema_str = json.dumps(response_schema, indent=2)
        
        full_prompt = f"""{prompt}

You MUST respond with valid JSON that matches this exact schema:
{schema_str}

Return ONLY the JSON object, no additional text or markdown formatting."""

        response = self.model.generate_content(full_prompt)
        text = response.text.strip()
        
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        return json.loads(text.strip())
    
    async def generate_plan(self, task: str, available_tools: list[dict]) -> dict:
        tools_description = "\n".join([
            f"- {tool['name']}: {tool['description']} (actions: {', '.join(tool['actions'])})"
            for tool in available_tools
        ])
        
        prompt = f"""You are a planning agent. Create a step-by-step execution plan for this task.

TASK: {task}

AVAILABLE TOOLS:
{tools_description}

Create a plan where each step uses one of the available tools. Be specific about parameters."""

        schema = {
            "type": "object",
            "properties": {
                "task_understanding": {"type": "string"},
                "steps": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "step_number": {"type": "integer"},
                            "description": {"type": "string"},
                            "tool": {"type": "string"},
                            "action": {"type": "string"},
                            "parameters": {"type": "object"}
                        }
                    }
                }
            }
        }
        
        return await self.generate_structured(prompt, schema)
    
    async def verify_results(self, original_task: str, plan: dict, results: list[dict]) -> dict:
        prompt = f"""You are a verification agent. Analyze the execution results and provide a final answer.

ORIGINAL TASK: {original_task}

EXECUTION PLAN:
{json.dumps(plan, indent=2)}

EXECUTION RESULTS:
{json.dumps(results, indent=2)}

Verify if the results are complete and provide a well-formatted final answer to the user's task."""

        schema = {
            "type": "object",
            "properties": {
                "is_complete": {"type": "boolean"},
                "missing_information": {"type": "array", "items": {"type": "string"}},
                "final_answer": {"type": "string"},
                "summary": {"type": "string"}
            }
        }
        
        return await self.generate_structured(prompt, schema)
