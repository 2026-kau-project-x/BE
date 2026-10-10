# BE (FastAPI)

Project X 백엔드. Trip Orchestrator(이동 상태머신) + AI 서비스 호출 + 영속화를 담당한다.
AI 서비스는 별도 리포(`AI`)이며, 외부에는 BE만 공개하고 AI는 내부망으로만 호출한다.

## 구조
```
app/
  main.py            앱 진입점, CORS(Flutter 웹)
  core/config.py     환경설정 (.env / 환경변수)
  api/v1/            라우터 (endpoints/health, trips)
  schemas/           요청·응답 모델 (pydantic)
  services/          도메인 로직 (trip_state 상태머신, ai_client)
  db/                SQLAlchemy 세션·모델 (SQLite → Postgres 이전 예정)
migrations/          Alembic 마이그레이션 (versions/0001_create_trips.py …)
tests/               pytest (conftest.py 에 공용 픽스처)
docker-compose.yml   BE + AI 로컬 통합 실행
```

## 실행
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate   /   macOS·Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env                 # Windows: copy .env.example .env
alembic upgrade head                 # DB 테이블 생성·갱신 (최초 1회 + 마이그레이션 추가 시마다)
uvicorn app.main:app --reload        # http://localhost:8000/docs
pytest
```

### AI 서비스와 같이 띄우기
- 직접 실행: AI 리포에서 `uvicorn app.main:app --port 8001` → BE `.env` 에 `AI_SERVICE_URL=http://localhost:8001`
- Docker: AI 리포를 `../AI` 에 clone 한 뒤 `docker compose up --build`

## DB 마이그레이션 (Alembic)
모델(`app/db/models.py`)을 바꿨으면:
```bash
alembic revision --autogenerate -m "설명"   # migrations/versions/ 에 파일 생성 → 내용 검토 후 커밋
alembic upgrade head
```
`tests/test_migrations.py` 가 "마이그레이션 결과 == 모델" 을 검사하므로, 생성을 잊으면 테스트가 실패한다.
`alembic.ini` 는 ASCII 만 쓸 것 (Windows 가 cp949 로 읽어 한글이 있으면 깨진다).

## API (v1)
| Method | Path | 설명 |
|---|---|---|
| GET | `/api/v1/health` | 헬스체크 |
| POST | `/api/v1/trips` | 이동 생성 (AI `/optimize` 로 랑데부 지점 제안) |
| GET | `/api/v1/trips/{id}` | 이동 조회 |
| PATCH | `/api/v1/trips/{id}/status` | 상태 전이 (허용되지 않으면 409) |

상태: `REQUESTED → WALKING ⇄ WAITING → RENDEZVOUS → COMPLETED` (각 단계에서 `CANCELLED` 가능)

### AI 연동 동작
- `AI_SERVICE_URL` 비어 있음 → `MockAiClient` (목적지 근처 고정 오프셋)
- 설정됨 → `HttpAiClient` 가 `POST {AI}/api/v1/optimize` 호출 (`walker`=출발지, `destination`=목적지)
- AI 오류·타임아웃(기본 3초) → **이동 생성은 성공**, `rendezvous_lat/lng` 만 `null` (안전 우선: AI 장애가 이동을 막지 않음)
- 차량 위치는 Dummy Vehicle API 연동 전이라 아직 보내지 않음 → AI 는 목적지를 랑데부로 반환

## 미구현 (다음 단계)
- 인증, Dummy Vehicle API 연동(차량 위치 → `/optimize` 의 `vehicle`), Postgres 전환
