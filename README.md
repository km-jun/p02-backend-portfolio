# 환경 공간데이터 관리·시각화 플랫폼 — 백엔드

환경 공간데이터 파일의 업로드, 공간 조회, 형식 변환 및 다운로드를 처리하는 FastAPI 기반 백엔드입니다.

학교 캡스톤 팀 프로젝트로 개발했습니다. 팀원 공동 작업물이 포함된 공개용 저장소입니다.

- **개발 기간:** 2026.03~2026.05
- **팀 구성:** 학생 4명, 멘토 1명
- **프론트엔드:** [p02-frontend-portfolio](https://github.com/km-jun/p02-frontend-portfolio)

## 주요 사용 기술

Python, FastAPI, PostgreSQL·PostGIS · 파일 저장: AWS S3

## 주요 기능

- 공간 데이터 파일 업로드 및 DB 저장
- 레이어 목록, GeoJSON 및 래스터 파일 URL 조회
- 지도 영역·지역·카테고리 조건에 따른 공간 조회
- 파일 형식 변환 및 다운로드 작업 상태 관리
- S3 파일 업로드 및 임시 다운로드 URL 생성

## 로컬 실행

Python, PostGIS가 활성화된 PostgreSQL DB와 S3 환경이 필요합니다.

```bash
git clone https://github.com/km-jun/p02-backend-portfolio.git
cd p02-backend-portfolio
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`.env`에서 DB·AWS 접속 정보를 설정합니다. 일부 기능은 코드에 고정된 S3 버킷·파일 경로도 변경해야 하므로 [실행·배포 상세 안내](docs/running.md)를 먼저 확인한 뒤 실행합니다.

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

환경변수·Windows 실행·API 문서·배포 설정은 [실행·배포 상세 안내](docs/running.md)를 참고하세요.

## 현재 상태

기존 AWS 무료 플랜 종료로 현재 운영 API는 제공하지 않습니다. 원래 개발 코드를 보존한 공개용 자료이며, 별도 DB·S3 환경에서의 설치와 통합 실행은 재검증하지 않았습니다.

## 관련 문서

- [실행·배포 상세 안내](docs/running.md)
- [개발 당시 팀 문서](docs/team-readme.md)
- [개발 이력 보존 및 공개용 정리 내역](docs/publication-notes.md)
