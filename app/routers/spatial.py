from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas import SpatialRequest
from app.services.spatial_service import get_spatial_data_service
from app.database import get_db

router = APIRouter(tags=["Spatial"])

@router.post("/query")
def get_spatial_data(
    request: SpatialRequest,
    db: Session = Depends(get_db)
):
    return get_spatial_data_service(request, db)