import sys, os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
    
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field
from objects.execution import Execution

from converse_style_orchestrator import process
app = FastAPI(title="Stateless Orchestration API", version="0.2.0")

# -----------------------------
# Request / Response Models
# -----------------------------
class OrchestrateRequest(BaseModel):
    key: str = Field(None, min_length=1, description="Jira issue key, e.g. ENG-123")
    prompt_version: str = Field(..., min_length=1, description="prompt version")
    seed: str = Field(None, description="Prompt or follow-up message")

class OrchestrationResult(BaseModel):
    key: str

# # Fire-and-forget orchestration: schedule background task and return immediately
# @app.post("/invokeAsync", response_model=OrchestrationResult)
# async def orchestrate(req: OrchestrateRequest, background_tasks: BackgroundTasks):
#     issue_key = req.issue_key
#     if not issue_key or not issue_key.strip():  # extra runtime validation for whitespace-only
#         raise HTTPException(status_code=400, detail="issue_key must not be empty")
#     seed = req.seed
#     background_tasks.add_task(process, issue_key, seed)
#     return OrchestrationResult(key=issue_key)

@app.post("/invoke", response_model=OrchestrationResult)
def orchestrate(req: OrchestrateRequest):
    key = req.key
    prompt_version = req.prompt_version
    seed = req.seed

    execution = process(prompt_version, key, seed)

    return OrchestrationResult(key=execution.key)

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=8000, reload=True)
