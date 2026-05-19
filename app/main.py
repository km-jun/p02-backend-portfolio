from fastapi import FastAPI
from app.database import engine, Base

from app.routers import download, upload, spatial

# DB 테이블 자동 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="EnvData Spatial API",
    description="공간 데이터 다운로드 / 업로드 / 조회 서비스",
    version="1.0.0"
)

# routers 등록
app.include_router(download.router, tags=["Download"])
app.include_router(upload.router, tags=["Upload"])
app.include_router(spatial.router, prefix="/spatial", tags=["Spatial"])

@app.get("/")
def read_root():
    return {"message": "EnvData API 서버가 정상적으로 실행 중입니다."}
