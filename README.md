# p02-backend

환경 공간데이터 통합 관리 및 시각화 플랫폼 - 백엔드

## 기술 스택
- Python 3.14
- FastAPI
- PostgreSQL + PostGIS
- SQLAlchemy + GeoAlchemy2
- GeoPandas, Shapely
- AWS S3 (boto3)
- Uvicorn
- python-dotenv

## 로컬 실행 방법
```bash
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API 목록
| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | / | 서버 상태 확인 |
| POST | /upload | 파일 업로드 + DB 저장 |
| GET | /layers | 레이어 목록 조회 |
| GET | /layers/{category}/geojson | 지도 표시용 GeoJSON |
| POST | /spatial/query | 다운로드 요청 |
| GET | /spatial/task/{id} | 작업 상태 확인 |

## 현재 구현 상태
- [x] DB 연결 (PostgreSQL + PostGIS)
- [x] 파일 업로드 API (GeoJSON, SHP, CSV)
- [x] 레이어 조회 API
- [x] 다운로드 API (CSV, EXCEL, SHP)
- [x] S3 업로드 및 Presigned URL
- [ ] 필터링 및 검색 API
- [ ] 업로드 진행률 모니터링 (WebSocket)

## 브랜치 전략
```
main
└── develop
    ├── feature/upload-api
    ├── feature/layer-api
    ├── feature/filter-search
    └── feature/progress-monitoring
```

### 브랜치 규칙
| 브랜치 | 용도 |
|--------|------|
| `main` | 배포용 브랜치 (EC2 운영 서버) |
| `develop` | 개발 통합 브랜치 |
| `feature/xxx` | 기능별 개발 브랜치 |

### 작업 흐름

#### 1. 최초 세팅 (처음 한 번만)
```bash
git clone https://github.com/km-jun/p02-backend.git
cd p02-backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### 2. 작업 시작할 때마다
```bash
# develop 브랜치로 이동 후 최신 코드 pull
git checkout develop
git pull origin develop

# 기능 브랜치 생성
git checkout -b feature/기능명
```

#### 3. 작업 완료 후
```bash
git add .
git commit -m "feat: 기능 설명"
git push origin feature/기능명
```

#### 4. Pull Request
1. GitHub에서 `p02-backend` 저장소 접속
2. **"Compare & pull request"** 클릭
3. base: `develop` ← compare: `feature/기능명` 확인
4. 제목과 설명 작성 후 **"Create pull request"** 클릭
5. 코드 리뷰 후 **"Merge pull request"** 클릭

#### 5. Merge 후 로컬 정리
```bash
git checkout develop
git pull origin develop
git branch -d feature/기능명
```

## 배포
- 서버: AWS EC2
- API 주소: http://52.79.237.230:8000
- API 문서: http://52.79.237.230:8000/docs
