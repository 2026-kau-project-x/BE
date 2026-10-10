# BE (FastAPI)

Project X 백엔드. Trip Orchestrator(이동 상태머신) + AI 서비스 호출 + 영속화를 담당한다.
AI 서비스는 별도 리포(`AI`)이며, 외부에는 BE만 공개하고 AI는 내부망으로만 호출한다.

## 구조
```
app/
  main.py            앱 진입점, lifespan(테이블 생성)
  core/config.py     환경설정 (.env / 환경변수)
  api/v1/            라우터 (endpoints/health, trips)
  schemas/           요청·응답 모델 (pydantic)
  services/          도메인 로직 (trip_state 상태머신, ai_client)
  db/                SQLAlchemy 세션·모델 (SQLite → Postgres 이전 예정)
tests/               pytest
```

## 실행
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload      # http://localhost:8000/docs
pytest
```

## API (v1)
| Method | Path | 설명 |
|---|---|---|
| GET | `/api/v1/health` | 헬스체크 |
| POST | `/api/v1/trips` | 이동 생성 (AI가 랑데부 지점 제안, 현재는 Mock) |
| GET | `/api/v1/trips/{id}` | 이동 조회 |
| PATCH | `/api/v1/trips/{id}/status` | 상태 전이 (허용되지 않으면 409) |

상태: `REQUESTED → WALKING ⇄ WAITING → RENDEZVOUS → COMPLETED` (각 단계에서 `CANCELLED` 가능)

## 미구현 (다음 단계)
- AI 서비스 연동 (`HttpAiClient`), Alembic 마이그레이션, 인증, Dummy Vehicle API 연동
