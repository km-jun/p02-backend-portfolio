# 환경 공간데이터 플랫폼 — 백엔드 포트폴리오

학교 캡스톤 팀 프로젝트의 백엔드 코드와 개발 이력을 공개하기 위한 저장소입니다. 공간 데이터 업로드·조회·변환·다운로드와 웹 지도 연동을 다룹니다.

- **원래 개발 기록:** 2026년 4월 30일~5월 30일의 커밋을 보존했습니다.
- **공개용 정리:** 2026년 10월. 새 저장소 생성일과 원래 개발 시기는 다릅니다.
- **작성자와 이력:** 팀원의 작성자 정보, 커밋 날짜·메시지, 브랜치와 병합 이력을 유지했습니다. 기존 GitHub PR·이슈 페이지는 이전하지 않았습니다.
- **서비스 상태:** 기존 AWS 무료 플랜 종료로 현재 운영 데모를 제공하지 않습니다. 코드를 실행하려면 별도의 DB·AWS 환경 설정이 필요합니다.
- **프론트엔드:** [p02-frontend](https://github.com/km-jun/p02-frontend)

## 본인 계정의 커밋에서 확인되는 변경 사항 — km-jun

이 저장소는 팀 프로젝트 전체의 결과물입니다. 아래는 `km-jun` 계정의 커밋에 포함된 변경 사항을 정리한 목록이며, 실제 담당 범위나 단독 설계·구현 여부를 확정한 목록은 아닙니다. 커밋 작성자 정보만으로는 팀원 코드의 통합 여부나 개발 도구의 도움을 받은 범위를 구분할 수 없습니다. 실제 역할은 추가 확인 후 정리할 예정입니다.

### 프론트엔드 및 API 연동
- React·Leaflet 기반 지도 화면과 GeoJSON 표시, 레이어 표시·숨김 기능
- 파일 업로드 API 연동, 업로드 진행률 표시, SHP ZIP 업로드 지원
- 카테고리·파일 형식·지역 선택 및 다운로드 처리 상태 표시
- 지도에서 선택한 사각형 영역을 다운로드 요청에 전달
- 지도 이동·확대 시 현재 화면 영역에 해당하는 데이터 조회 API 연동

### 백엔드 기능 보완
- 레이어 목록 조회 API 및 파일 형식 정보 추가
- 업로드 파일 구분과 카테고리 입력 검증 보완
- SHP 결과 폴더를 ZIP으로 압축해 S3에 업로드하도록 수정
- SHP 다운로드 임시 폴더 삭제 오류 수정
- 팀원이 작성한 공간 조회 로직을 서비스에 통합하고 프론트엔드와 연동

파일 변환 핵심 로직, 데이터 적재 최적화, TIF 렌더링 최적화 등에는 팀원 계정의 작성 기록이 있습니다. 프로젝트 전체를 본인의 단독 구현으로 주장하지 않으며, 변경 이력은 커밋별 작성자와 코드 차이를 참고해 주세요.

## 보안 정리

과거 커밋에 포함된 로컬 DB 비밀번호를 `YOUR_DB_PASSWORD`라는 예시 값으로 교체했습니다. 이에 따라 커밋 ID는 변경되었지만 기존 작성자·날짜·메시지와 코드 변경 이력은 보존했습니다. 최신 애플리케이션 코드는 유지하고 공개용 README 설명만 추가했습니다.

---

## 기존 프로젝트 문서

아래는 개발 당시 작성한 문서입니다. 진행 상태·운영 주소·향후 계획은 당시 기록이며 현재 서비스 운영을 의미하지 않습니다.

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
| POST | /spatial/search | 지도 영역(BBox) 기반 벡터 데이터 검색 |
| GET | /layers/{category}/raster | TIF 래스터 이미지 S3 임시 다운로드 URL 반환 |
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
git clone https://github.com/km-jun/p02-backend-portfolio.git
cd p02-backend-portfolio
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
- [x] 공간 데이터 인덱스(GIST) 구축 및 쿼리 최적화
- [x] TIF 래스터 파일 프론트엔드 히트맵 시각화 연동
- [x] 대용량 GeoJSON 단순화(ST_Simplify) 적용

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

> 보안 정리: 과거 커밋에 포함된 로컬 DB 비밀번호를 예시 값으로 교체했습니다. 이 과정에서 커밋 ID가 변경되었으며, 기존 작성자·날짜·작업 내용은 유지했습니다.
