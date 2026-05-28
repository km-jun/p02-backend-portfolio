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

---

## 현재 진행 상황 (2026.05.18)

### 완료된 기능
- [x] PostgreSQL + PostGIS 연결
- [x] GeoJSON 파일 업로드 및 DB 저장
- [x] CSV 파일 업로드 및 DB 저장
- [x] SHP(ZIP) 파일 업로드 및 DB 저장
- [x] Timestamp 직렬화 처리 (날짜 필드 자동 변환)
- [x] 파일명 특수문자 처리 (category 필드)
- [x] 레이어 목록 조회 API
- [x] 레이어 GeoJSON 조회 API (지도 렌더링용)
- [x] CORS 설정 (localhost, Vercel)
- [x] S3 업로드 및 Presigned URL 생성
- [x] 다운로드 API (CSV, Excel, SHP)

### 주요 엔드포인트

**데이터 업로드**:
- `POST /upload` - 파일 업로드 (multipart/form-data)
  - 지원 형식: GeoJSON, CSV, SHP(ZIP)
  - 자동 geometry 변환 및 DB 저장

**데이터 조회**:
- `GET /layers` - 전체 레이어 목록
- `GET /layers/{category}/geojson` - 특정 레이어 GeoJSON

**데이터 다운로드**:
- `POST /spatial/query` - 다운로드 요청
- `GET /spatial/task/{id}` - 작업 상태 확인

### 데이터베이스 구조

**spatial_data 테이블**:
- `id` - Primary Key
- `category` - 레이어 구분자
- `geom` - PostGIS Geometry
- `properties` - JSONB (속성 정보)
- `created_at` - 생성 시간

**file_records 테이블**:
- `id` - Primary Key
- `original_name` - 원본 파일명
- `s3_key` - S3 저장 경로
- `record_count` - 레코드 수
- `uploaded_at` - 업로드 시간

### 배포 정보

**서버**: AWS EC2 (Ubuntu)
- **API 주소**: `http://52.79.237.230:8000`
- **API 문서**: `http://52.79.237.230:8000/docs`
- **데이터베이스**: AWS RDS (PostgreSQL + PostGIS)

### 알려진 이슈

**HTTP 프로토콜 사용 중**
- **문제**: Vercel(HTTPS)에서 접근 시 Mixed Content Error
- **해결**: HTTPS 설정 필요 (도메인 + SSL 인증서)
- **현재**: localhost에서는 정상 작동

### 다음 단계

1. [ ] 도메인 구매 및 DNS 설정
2. [ ] Nginx + Let's Encrypt SSL 인증서 설치
3. [ ] HTTPS(443 포트) 리버스 프록시 설정
4. [ ] 레이어 필터링 API 추가
5. [ ] 검색 API (속성 기반)
6. [ ] 업로드 진행률 WebSocket

### 환경 변수

`.env` 파일 (EC2에만 존재, Git에 미포함):
```bash
DATABASE_URL=postgresql://...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
S3_BUCKET_NAME=...
```

### 의존성 관리

**가상환경 규칙**:
- `.venv/` 폴더는 `.gitignore`에 포함
- 각 환경에서 독립적으로 생성
- `requirements.txt`로 의존성 관리

### 관련 저장소
- 프론트엔드: [km-jun/p02-frontend](https://github.com/km-jun/p02-frontend)