import boto3
import os
import re
import tempfile
import uuid as uuid_lib
import json
from typing import Optional
from botocore.config import Config

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
import rasterio

from app.database import get_db
from app.models import File as FileModel, SpatialData
from app.schemas import UploadResponse, FileResponse
from app.services.file_parser import SUPPORTED_EXTENSIONS, parse_upload_file
from app.services.s3_uploader import upload_to_s3

router = APIRouter()

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
_CATEGORY_RE = re.compile(r'^[a-zA-Z0-9가-힣\s_\-\(\)]{1,50}$')

ALLOWED_EXTENSIONS = set(SUPPORTED_EXTENSIONS) | {".tif", ".tiff"}


@router.post("/upload", response_model=UploadResponse)
async def upload_spatial_file(
        file: UploadFile = File(..., description="SHP(ZIP), GeoJSON, CSV, TIF 파일"),
        category: str = Form(..., description="레이어 분류명 (예: 지하수, 수질)"),
        region_name: Optional[str] = Form(None, description="지역명 (예: 서울)"),
        db: Session = Depends(get_db),
):
    if not _CATEGORY_RE.match(category):
        raise HTTPException(
            status_code=422,
            detail="category는 1~50자의 영문, 한글, 숫자, _, - 만 허용됩니다.",
        )

    original_name = file.filename or "upload"
    file_ext = os.path.splitext(original_name)[1].lower()

    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"지원하지 않는 파일 형식입니다. 허용: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="파일 크기는 100MB를 초과할 수 없습니다.")

    tmp_path: Optional[str] = None
    file_record: Optional[FileModel] = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        # 1. S3에 원본 파일 저장 (uploads/ prefix)
        unique_name = f"{uuid_lib.uuid4().hex}_{original_name}"
        s3_key = upload_to_s3(tmp_path, unique_name, prefix="uploads")

        # 2. FILES 테이블에 ORIGINAL 기록
        file_record = FileModel(
            file_name=original_name,
            file_size=len(contents),
            format=file_ext.lstrip(".").upper(),
            s3_path=s3_key,
            file_type="UPLOAD",
        )
        db.add(file_record)
        db.commit()
        db.refresh(file_record)

        # 3. TIF와 벡터(SHP, CSV 등) 처리 로직 분기
        if file_ext in [".tif", ".tiff"]:
            # TIF 파일: rasterio로 메타데이터 추출 후 DB에 즉시 적재
            with rasterio.open(tmp_path) as src:
                metadata = {
                    "width": src.width,
                    "height": src.height,
                    "bounds": list(src.bounds),
                    "crs": str(src.crs),
                    "pixel_size": [src.transform[0], abs(src.transform[4])],
                    "s3_path": s3_key  # 추후 다운로드 연동을 위해 S3 주소 보관
                }

            spatial_record = SpatialData(
                category=category,
                properties=metadata,
                original_file_id=file_record.id,
                region_name=region_name,
                geom=None
            )
            db.add(spatial_record)
            db.commit()
            record_count = 1
        else:
            record_count = parse_upload_file(
                file_path=tmp_path,
                file_ext=file_ext,
                category=category,
                region_name=region_name,
                file_id=file_record.id,
                db=db,
            )

        return UploadResponse(
            file_id=file_record.id,
            file_name=original_name,
            record_count=record_count,
            category=category,
            message=f"업로드 완료. {record_count}개의 데이터가 저장되었습니다.",
        )

    except HTTPException:
        raise
    except (ValueError, RuntimeError) as e:
        if file_record:
            db.delete(file_record)
            db.commit()
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        if file_record:
            try:
                db.delete(file_record)
                db.commit()
            except Exception:
                pass
        raise HTTPException(status_code=500, detail=f"업로드 처리 중 오류: {str(e)}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


@router.get("/spatial/files", response_model=list[FileResponse])
def list_files(file_type: Optional[str] = None, limit: int = 20, offset: int = 0, db: Session = Depends(get_db)):
    query = db.query(FileModel).order_by(FileModel.created_at.desc())
    if file_type:
        query = query.filter(FileModel.file_type == file_type)
    return query.offset(offset).limit(limit).all()


@router.get("/layers/{category}/geojson")
def get_layer_geojson(category: str, db: Session = Depends(get_db)):
    from app.models import SpatialData
    from geoalchemy2.shape import to_shape
    from sqlalchemy import func
    from fastapi import HTTPException

    rows = db.query(
        func.ST_Simplify(SpatialData.geom, 0.0001).label('geom'),
        SpatialData.properties
    ).filter(
        SpatialData.category == category,
        SpatialData.geom.isnot(None) # 빈 공간 데이터는 제외
    ).all()

    if not rows:
        raise HTTPException(status_code=404, detail="해당 카테고리 데이터가 없습니다.")

    features = []
    for row in rows:
        if row.geom is None:
            continue

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


@router.get("/layers")
def get_layer_list(db: Session = Depends(get_db)):
    from sqlalchemy import distinct
    from app.models import SpatialData, File

    results = db.query(
        SpatialData.category,
        File.file_type
    ).join(
        File, SpatialData.original_file_id == File.id
    ).distinct(SpatialData.category).all()

    return [{"category": row[0], "file_type": row[1]} for row in results if row[0]]


@router.get("/layers/{category}/raster")
def get_raster_url(category: str, db: Session = Depends(get_db)):
    """TIF 파일 시각화를 위한 S3 임시 다운로드 URL 반환"""
    from app.models import SpatialData
    from fastapi import HTTPException
    import boto3
    import os

    row = db.query(SpatialData).filter(SpatialData.category == category).first()

    s3_key = None

    if row and row.properties and 's3_path' in row.properties:
        s3_key = row.properties['s3_path']
    else:
        TIF_S3_MAPPING = {
            "연간 지하수 재충전": "tif/연간_지하수_재충전(annual_Recharge)/annual_recharge.tif",
            "지표수 유기오염": "tif/IDW_Q_지표수 유기오염물질.tif",
            "지하수 질산성질소": "tif/IDW_Q_지하수질산염.tif",
            "해수침투 지수": "tif/Idw_Q_해수침투1.tif"
        }
        if category not in TIF_S3_MAPPING:
            raise HTTPException(status_code=404, detail="래스터 정보를 찾을 수 없습니다.")
        s3_key = TIF_S3_MAPPING[category]

    # S3 Presigned URL 생성 (1시간 유효)
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name='ap-northeast-2',
        endpoint_url='https://s3.ap-northeast-2.amazonaws.com',
        config=Config(signature_version='s3v4')
    )
    bucket = "envdata-export-336093158879-ap-northeast-2-an"

    presigned_url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket, 'Key': s3_key},
        ExpiresIn=3600
    )

    return {"url": presigned_url}


@router.delete("/layers/{category}")
def delete_user_layer(category: str, db: Session = Depends(get_db)):
    """사용자가 업로드한 레이어를 DB와 S3에서 완전히 삭제합니다."""
    import boto3
    import os

    # 1. 공간 데이터(SpatialData) 조회
    spatial_records = db.query(SpatialData).filter(SpatialData.category == category).all()
    if not spatial_records:
        raise HTTPException(status_code=404, detail="삭제할 레이어를 찾을 수 없습니다.")

    # 2. 원본 파일(FileModel) 메타데이터 조회
    original_file_id = spatial_records[0].original_file_id
    file_record = db.query(FileModel).filter(FileModel.id == original_file_id).first()

    # 3. AWS S3에서 실제 파일 삭제
    if file_record and file_record.s3_path:
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name='ap-northeast-2'
            )
            bucket = "envdata-export-336093158879-ap-northeast-2-an"
            s3_client.delete_object(Bucket=bucket, Key=file_record.s3_path)
        except Exception as e:
            print(f"S3 파일 삭제 실패 (무시하고 DB 삭제 진행): {e}")

    # 4. DB 테이블 삭제
    try:
        for record in spatial_records:
            db.delete(record)

        if file_record:
            db.delete(file_record)

        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"DB 데이터 삭제 중 오류 발생: {str(e)}")

    return {"message": f"{category} 레이어가 성공적으로 삭제되었습니다."}