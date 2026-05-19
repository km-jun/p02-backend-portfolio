from pydantic import BaseModel, field_validator
from typing import Optional


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