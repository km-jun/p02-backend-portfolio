# 로컬 실행과 배포

## 로컬 실행 준비

Python 3.10 이상과 PostGIS 확장이 활성화된 PostgreSQL DB, 접근 가능한 S3 버킷이 필요합니다. 고정된 패키지들의 전체 설치는 재검증하지 않았으며, Python 버전과 운영체제에 따라 추가 호환성 확인이 필요합니다.

```bash
git clone https://github.com/km-jun/p02-backend-portfolio.git
cd p02-backend-portfolio
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows 명령 프롬프트에서는 `.venv\Scripts\activate.bat`, PowerShell에서는 `.\.venv\Scripts\Activate.ps1`로 가상환경을 활성화합니다.

프로젝트 루트에 `.env`를 만들고 자신의 환경에 맞게 아래 값을 설정하세요. 대괄호로 표시한 내용은 예시이며 실제 값으로 교체해야 합니다.

```dotenv
DATABASE_URL=postgresql://[DB_USER]:[DB_PASSWORD]@[DB_HOST]:5432/[DB_NAME]
AWS_ACCESS_KEY_ID=[YOUR_ACCESS_KEY]
AWS_SECRET_ACCESS_KEY=[YOUR_SECRET_KEY]
AWS_REGION=ap-northeast-2
S3_BUCKET_NAME=[YOUR_BUCKET_NAME]
```

DB는 미리 생성하고 PostGIS 확장을 활성화해야 합니다. 앱은 시작할 때 모델의 테이블을 생성하므로 DB 계정에 테이블 생성 권한도 필요합니다.

**S3 설정 주의:** `S3_BUCKET_NAME`과 `AWS_REGION`은 업로드 모듈에서 사용하지만, 다음 경로에는 기존 버킷·리전·파일 경로가 코드에 고정되어 있습니다. `.env` 설정만으로 모든 기능이 새 S3 환경으로 전환되지는 않습니다.

- `app/services/data_export_service.py`: `export_bucket`, `TIF_S3_MAPPING`, S3 리전
- `app/routers/upload.py`: 래스터 조회·레이어 삭제의 버킷과 리전, 래스터 파일 매핑

변환·다운로드·래스터 조회·파일 삭제를 실행하려면 이 값들을 자신의 테스트용 S3 환경에 맞춰 수정하고 필요한 TIF 파일을 준비해야 합니다.

`.env`와 실제 접속 정보는 Git에 올리지 않습니다. 프론트엔드와 연결할 때는 `app/main.py`의 CORS 허용 출처도 실행 주소에 맞춰 확인하세요.

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

실행 후 API 문서는 [http://localhost:8000/docs](http://localhost:8000/docs)에서 확인할 수 있습니다.

## 배포 시 확인할 설정

- 배포 환경에 맞는 DB 접속 정보와 S3 접근 권한을 설정합니다.
- 프론트엔드가 HTTPS로 배포됐다면 백엔드에도 HTTPS 주소가 필요합니다.
- `app/main.py`의 CORS 허용 출처에 프론트엔드 주소를 반영합니다.
- 위의 `--reload` 실행 명령은 로컬 개발용입니다. 실제 운영에는 별도의 프로세스 관리와 HTTPS 설정이 필요합니다.

현재 운영 서버를 복원한 상태는 아니며, 별도 DB·S3 환경에서 설치와 통합 실행을 재검증하지 않았습니다.

[README로 돌아가기](../README.md)
