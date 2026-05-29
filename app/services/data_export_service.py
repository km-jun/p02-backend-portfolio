import os

if "PROJ_LIB" in os.environ:
    del os.environ["PROJ_LIB"]
if "PROJ_DATA" in os.environ:
    del os.environ["PROJ_DATA"]

import json
import logging
import boto3
from datetime import datetime
import pandas as pd
import geopandas as gpd
from sqlalchemy import create_engine, text
from shapely import wkt
import rasterio
from rasterio.mask import mask
from shapely.geometry import box
from rasterio.warp import transform_bounds

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(BASE_DIR, '.env')

# 환경 변수 로드
if os.path.exists(env_path):
    from dotenv import load_dotenv

    load_dotenv(dotenv_path=env_path, override=True)

DB_URL = os.getenv("DATABASE_URL")
engine = create_engine(DB_URL) if DB_URL else None


class DataExportService:
    TIF_S3_MAPPING = {
        "연간 지하수 재충전": "s3://envdata-export-336093158879-ap-northeast-2-an/tif/연간_지하수_재충전(annual_Recharge)/annual_recharge.tif",
        "지표수 유기오염": "s3://envdata-export-336093158879-ap-northeast-2-an/tif/IDW_Q_지표수 유기오염물질.tif",
        "지하수 질산성질소": "s3://envdata-export-336093158879-ap-northeast-2-an/tif/IDW_Q_지하수질산염.tif",
        "해수침투 지수": "s3://envdata-export-336093158879-ap-northeast-2-an/tif/Idw_Q_해수침투1.tif"
    }

    def __init__(self, db_engine=None):
        self.engine = db_engine or engine
        if not self.engine:
            raise ValueError("❌ DATABASE_URL 환경 변수가 설정되지 않았거나 엔진이 없습니다.")

        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name='ap-northeast-2'
        )
        self.export_bucket = "envdata-export-336093158879-ap-northeast-2-an"

    def export_spatial_data(self, task_id: str, category: str, target_format: str, bbox: list = None,
                            filters: dict = None) -> str:
        logger.info(f"[Task ID: {task_id}] 백그라운드 파일 생성 작업을 시작합니다...")
        logger.info(f"[데이터 추출 시작] 카테고리: {category}, 포맷: {target_format.upper()}")

        if target_format.upper() == 'TIF':
            try:
                result = self._export_raster(task_id, category, bbox)
                logger.info(f"✅ [Task ID: {task_id}] TIF 파일 생성 및 S3 업로드 완료")
                return json.dumps({
                    "status": "SUCCESS",
                    "file_path": result['file_path'],
                    "download_url": result['download_url']
                }, ensure_ascii=False)
            except Exception as e:
                logger.error(f"❌ [Task ID: {task_id}] TIF 작업 실패: {e}")
                return json.dumps({"status": "FAILED", "error": str(e)}, ensure_ascii=False)

        try:
            query_str = """
                SELECT id, category, properties, region_name, ST_AsText(geom) as geom_wkt
                FROM spatial_data
                WHERE category = :category
            """
            params = {"category": category}

            if bbox and len(bbox) == 4:
                query_str += """
                    AND ST_Intersects(
                        geom, 
                        ST_MakeEnvelope(:min_x, :min_y, :max_x, :max_y, 4326)
                    )
                """
                params.update({"min_x": bbox[0], "min_y": bbox[1], "max_x": bbox[2], "max_y": bbox[3]})
            elif filters and filters.get("region_name"):
                query_str += " AND region_name = :region_name"
                params["region_name"] = filters["region_name"]

            with self.engine.connect() as conn:
                df = pd.read_sql(text(query_str), conn, params=params)

            if df.empty:
                error_msg = f"'{category}'에 해당하는 데이터가 없습니다."
                logger.error(f"❌ [Task ID: {task_id}] 작업 실패: {error_msg}")
                return json.dumps({"status": "FAILED", "error": error_msg}, ensure_ascii=False)

            df['properties'] = df['properties'].apply(lambda x: json.loads(x) if isinstance(x, str) else x)
            df['geometry'] = df['geom_wkt'].apply(lambda x: wkt.loads(x) if x else None)
            gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")

            props_df = pd.json_normalize(gdf['properties'])
            gdf = pd.concat([gdf.drop(columns=['properties', 'geom_wkt']), props_df], axis=1)
            gdf = gpd.GeoDataFrame(gdf, geometry='geometry', crs="EPSG:4326")

            export_dir = os.path.join(BASE_DIR, "exports")
            os.makedirs(export_dir, exist_ok=True)

            file_name = f"export_{category}_{task_id}"
            fmt = target_format.upper()

            if fmt == "GEOJSON":
                output_path = os.path.join(export_dir, f"{file_name}.geojson")
                gdf.to_file(output_path, driver="GeoJSON", encoding="utf-8")
            elif fmt == "SHP":
                output_path = os.path.join(export_dir, file_name)
                gdf.to_file(output_path, driver="ESRI Shapefile", encoding="utf-8")
            elif fmt == "CSV":
                output_path = os.path.join(export_dir, f"{file_name}.csv")
                if gdf.geometry.iloc[0].geom_type == 'Point':
                    gdf['경도'] = gdf.geometry.x
                    gdf['위도'] = gdf.geometry.y
                else:
                    gdf['wkt_geometry'] = gdf.geometry.apply(lambda g: g.wkt if g else "")
                df_out = pd.DataFrame(gdf.drop(columns=['geometry']))
                df_out.to_csv(output_path, index=False, encoding="utf-8-sig")
            elif fmt == "EXCEL":
                output_path = os.path.join(export_dir, f"{file_name}.xlsx")
                if gdf.geometry.iloc[0].geom_type == 'Point':
                    gdf['경도'] = gdf.geometry.x
                    gdf['위도'] = gdf.geometry.y
                else:
                    gdf['wkt_geometry'] = gdf.geometry.apply(lambda g: g.wkt if g else "")
                df_out = pd.DataFrame(gdf.drop(columns=['geometry']))
                df_out.to_excel(output_path, index=False)
            else:
                raise ValueError(f"❌ 지원하지 않는 포맷입니다: {target_format}")

            logger.info(f"✅ [Task ID: {task_id}] 파일 생성 완료: {output_path}")
            return json.dumps({"status": "SUCCESS", "file_path": output_path}, ensure_ascii=False)

        except Exception as e:
            logger.error(f"❌ [Task ID: {task_id}] 작업 중 내부 시스템 에러 발생: {e}")
            return json.dumps({"status": "FAILED", "error": str(e)}, ensure_ascii=False)

    def _export_raster(self, task_id: str, category: str, bbox: list):
        if category not in self.TIF_S3_MAPPING:
            raise ValueError(f"지원하지 않는 래스터 카테고리입니다: {category}")

        if not bbox or len(bbox) != 4:
            raise ValueError("TIF 파일 추출은 반드시 BBox(영역 지정)가 필요합니다.")

        s3_uri = self.TIF_S3_MAPPING[category]

        # 로컬 임시 저장 폴더 설정
        export_dir = os.path.join(BASE_DIR, "exports")
        os.makedirs(export_dir, exist_ok=True)
        generated_file_path = os.path.join(export_dir, f"{task_id}_{category}.tif")

        try:
            min_lng, min_lat, max_lng, max_lat = bbox

            with rasterio.Env(AWS_NO_SIGN_REQUEST=False, GTIFF_SRS_SOURCE="EPSG"):
                with rasterio.open(s3_uri) as src:
                    raster_crs = src.crs

                    minx, miny, maxx, maxy = transform_bounds(
                        'EPSG:4326', raster_crs,
                        min_lng, min_lat, max_lng, max_lat
                    )
                    geom_proj = box(minx, miny, maxx, maxy)

                    out_image, out_transform = mask(src, [geom_proj], crop=True)
                    out_meta = src.meta.copy()

                    out_meta.update({
                        "driver": "GTiff",
                        "height": out_image.shape[1],
                        "width": out_image.shape[2],
                        "transform": out_transform
                    })

                    with rasterio.open(generated_file_path, "w", **out_meta) as dest:
                        dest.write(out_image)

            # S3에 업로드
            s3_key = f"exports/{task_id}_{category}.tif"
            self.s3_client.upload_file(generated_file_path, self.export_bucket, s3_key)

            # 1시간 'URL' 생성
            download_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.export_bucket, 'Key': s3_key},
                ExpiresIn=3600
            )

            return {
                "file_path": generated_file_path,
                "s3_path": s3_key,
                "download_url": download_url,
                "format": "TIF"
            }

        except ValueError as e:
            if "Input shapes do not overlap raster" in str(e):
                raise ValueError("선택하신 영역에는 래스터 데이터가 존재하지 않습니다.")
            raise e