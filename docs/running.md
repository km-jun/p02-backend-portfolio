# 로컬 실행과 배포

## 로컬 실행 준비

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


## 배포 시 확인할 설정

- 배포 환경에 맞는 DB 접속 정보와 S3 접근 권한을 설정합니다.
- 프론트엔드가 HTTPS로 배포됐다면 백엔드에도 HTTPS 주소가 필요합니다.
- `app/main.py`의 CORS 허용 출처에 프론트엔드 주소를 반영합니다.
- 위의 `--reload` 실행 명령은 로컬 개발용입니다. 실제 운영에는 별도의 프로세스 관리와 HTTPS 설정이 필요합니다.

현재 운영 서버를 복원한 상태는 아니며, 별도 DB·S3 환경에서 설치와 통합 실행을 재검증하지 않았습니다.

[프로젝트 소개로 돌아가기](../README.md)
