import re
from datetime import datetime
from typing import Dict, Literal, Optional, List

from pydantic import BaseModel, field_validator


class DownloadRequest(BaseModel):
    category: str
    target_format: Literal["CSV", "EXCEL", "SHP", "GEOJSON"]
    region_name: Optional[str] = None
    filters: Optional[Dict[str, str]] = None
    bbox: Optional[List[float]] = None

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9가-힣\s_\-\(\)]{1,50}$', v):
            raise ValueError("category는 1~50자의 영문, 한글, 숫자, 공백, _, -, (, ) 만 허용됩니다.")
        return v


class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    target_format: str
    progress: int = 0
    download_url: Optional[str] = None


class UploadResponse(BaseModel):
    file_id: int
    file_name: str
    record_count: int
    category: str
    message: str

class FileResponse(BaseModel):
    id: int
    file_name: str
    format: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SpatialRequest(BaseModel):
    region_name: Optional[str] = None
    category: Optional[str] = None
    minLng: Optional[float] = None
    minLat: Optional[float] = None
    maxLng: Optional[float] = None
    maxLat: Optional[float] = None
    limit: Optional[int] = 100

    @field_validator("maxLat")
    @classmethod
    def bbox_check(cls, v, values):
        minLat = values.data.get("minLat")
        minLng = values.data.get("minLng")
        maxLng = values.data.get("maxLng")
        maxLat = v
        if not all([minLat, minLng, maxLat, maxLng]):
            return v
        if not (-90 <= minLat <= 90 and -90 <= maxLat <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        if not (-180 <= minLng <= 180 and -180 <= maxLng <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        if minLat > maxLat:
            raise ValueError("minLat cannot be greater than maxLat")
        if minLng > maxLng:
            raise ValueError("minLng cannot be greater than maxLng")
        return v

    @field_validator("limit")
    @classmethod
    def limit_check(cls, v):
        if v and v > 1000:
            return 1000
        if v and v <= 0:
            return 100
        return v