# 환경 공간데이터 관리·시각화 플랫폼 — 백엔드

환경 공간데이터 파일의 업로드, 공간 조회, 형식 변환 및 다운로드를 처리하는 FastAPI 기반 백엔드입니다.

학교 캡스톤 팀 프로젝트로 개발했습니다. 팀원 공동 작업물이 포함된 공개용 저장소입니다.

- **개발 기간:** 2026.03~2026.05
- **팀 구성:** 학생 4명, 멘토 1명
- **프론트엔드:** [p02-frontend-portfolio](https://github.com/km-jun/p02-frontend-portfolio)

## 사용 기술

Python, FastAPI, PostgreSQL·PostGIS, SQLAlchemy, GeoAlchemy2, GeoPandas, Shapely, boto3, AWS S3, Uvicorn

## 주요 기능

- 공간 데이터 파일 업로드 및 DB 저장
- 레이어 목록, GeoJSON 및 래스터 파일 URL 조회
- 지도 영역·지역·카테고리 조건에 따른 공간 조회
- 파일 형식 변환 및 다운로드 작업 상태 관리
- S3 파일 업로드 및 임시 다운로드 URL 생성

## 로컬 실행

Python 환경과 PostGIS 확장이 활성화된 PostgreSQL DB, 접근 가능한 S3 버킷이 필요합니다.

```bash
git clone https://github.com/km-jun/p02-backend-portfolio.git
cd p02-backend-portfolio
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows에서는 `source` 명령 대신 `.venv\Scripts\activate`로 가상환경을 활성화합니다.

프로젝트 루트에 `.env`를 만들고 자신의 환경에 맞게 아래 값을 설정하세요. 대괄호로 표시한 내용은 예시이며 실제 값으로 교체해야 합니다.

```dotenv
DATABASE_URL=postgresql://[DB_USER]:[DB_PASSWORD]@[DB_HOST]:5432/[DB_NAME]
AWS_ACCESS_KEY_ID=[YOUR_ACCESS_KEY]
AWS_SECRET_ACCESS_KEY=[YOUR_SECRET_KEY]
AWS_REGION=ap-northeast-2
S3_BUCKET_NAME=[YOUR_BUCKET_NAME]
```

`.env`와 실제 접속 정보는 Git에 올리지 않습니다. 프론트엔드와 연결할 때는 `app/main.py`의 CORS 허용 출처도 실행 주소에 맞춰 확인하세요.

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

실행 후 API 문서는 [http://localhost:8000/docs](http://localhost:8000/docs)에서 확인할 수 있습니다.

## 현재 상태

기존 AWS 무료 플랜 종료로 현재 운영 API는 제공하지 않습니다. 원래 개발 코드를 보존한 공개용 자료이며, 별도 DB·S3 환경에서의 설치와 통합 실행은 재검증하지 않았습니다.

## 공개용 정리

과거 커밋의 로컬 DB 비밀번호를 예시 값으로 교체했습니다. 작성자·작업 날짜·커밋 메시지와 개발 이력은 보존했으며, 정리 과정에서 커밋 ID가 변경됐습니다. 원본 PR·이슈·댓글은 이전하지 않았습니다.
