from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import datetime

class EvolutionLogEntry(BaseModel):
    id: str
    agent_name: str
    stage: str
    status: str
    training_run_id: Optional[str] = None
    example_count: Optional[int] = None
    baseline_score: Optional[float] = None
    new_score: Optional[float] = None
    analysis_summary: Optional[str] = None
    created_at: datetime.datetime

class EvolutionWebhookRequest(BaseModel):
    id: str
    status: str
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
