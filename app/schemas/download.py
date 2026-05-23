from pydantic import BaseModel
from typing import Dict, Literal, Optional


class DownloadRequest(BaseModel):
    category: str
    target_format: Literal["CSV", "EXCEL", "SHP"]
    filters: Optional[Dict[str, str]] = None


class TaskResponse(BaseModel):
    task_id: int
    status: str
    message: str