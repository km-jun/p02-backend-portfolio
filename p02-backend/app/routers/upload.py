import os
import shutil
import tempfile
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
import geopandas as gpd
from app.database import get_db
from app.models import File as FileModel, SpatialData

router = APIRouter()

ALLOWED_EXTENSIONS = {".geojson", ".json", ".shp", ".zip", ".csv"}

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    category: str = "default",
    db: Session = Depends(get_db)
):
    # 확장자 확인
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"지원하지 않는 파일 형식입니다: {ext}")

    # 임시 파일로 저장
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        # GeoDataFrame으로 읽기
        if ext in [".geojson", ".json"]:
            gdf = gpd.read_file(tmp_path)
        elif ext == ".zip":  # SHP zip
            gdf = gpd.read_file(f"zip://{tmp_path}")
        elif ext == ".csv":
            import pandas as pd
            df = pd.read_csv(tmp_path)
            if "geometry" not in df.columns and ("lat" not in df.columns or "lon" not in df.columns):
                raise HTTPException(status_code=400, detail="CSV에 geometry 또는 lat/lon 컬럼이 필요합니다.")
            from shapely.geometry import Point
            gdf = gpd.GeoDataFrame(
                df,
                geometry=[Point(row.lon, row.lat) for _, row in df.iterrows()],
                crs="EPSG:4326"
            )
        else:
            gdf = gpd.read_file(tmp_path)

        # CRS 변환 (WGS84로 통일)
        if gdf.crs is None:
            gdf = gdf.set_crs("EPSG:4326")
        else:
            gdf = gdf.to_crs("EPSG:4326")

        # Files 테이블에 기록
        file_record = FileModel(
            file_name=file.filename,
            file_size=os.path.getsize(tmp_path),
            format=ext.replace(".", "").upper(),
            file_type="UPLOAD"
        )
        db.add(file_record)
        db.commit()
        db.refresh(file_record)

        # SpatialData 테이블에 각 행 저장
        count = 0
        for _, row in gdf.iterrows():
            if row.geometry is None:
                continue
            spatial = SpatialData(
                original_file_id=file_record.id,
                category=category,
                geom=f"SRID=4326;{row.geometry.wkt}",
                properties={k: str(v) for k, v in row.drop("geometry").items()},
                region_name=row.get("region_name", None)
            )
            db.add(spatial)
            count += 1

        db.commit()

        return {
            "message": "업로드 성공",
            "file_id": file_record.id,
            "file_name": file.filename,
            "category": category,
            "feature_count": count
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"처리 중 오류: {str(e)}")
    finally:
        os.unlink(tmp_path)


@router.get("/layers")
def get_layers(db: Session = Depends(get_db)):
    """업로드된 레이어 목록 조회"""
    from sqlalchemy import func
    results = db.query(
        SpatialData.category,
        func.count(SpatialData.id).label("count")
    ).group_by(SpatialData.category).all()

    return [{"category": r.category, "count": r.count} for r in results]


@router.get("/layers/{category}/geojson")
def get_layer_geojson(category: str, db: Session = Depends(get_db)):
    """특정 레이어의 GeoJSON 반환 (지도 표시용)"""
    rows = db.query(SpatialData).filter(SpatialData.category == category).all()
    if not rows:
        raise HTTPException(status_code=404, detail="해당 카테고리 데이터가 없습니다.")

    features = []
    for row in rows:
        from geoalchemy2.shape import to_shape
        geom = to_shape(row.geom)
        features.append({
            "type": "Feature",
            "geometry": geom.__geo_interface__,
            "properties": row.properties
        })

    return {
        "type": "FeatureCollection",
        "features": features
    }
