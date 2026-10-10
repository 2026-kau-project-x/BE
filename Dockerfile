FROM python:3.12-slim
WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY alembic.ini .
COPY migrations ./migrations
EXPOSE 8000
# 기동 시 마이그레이션 적용 후 서버 실행.
# (Phase 4 ECS 에서 태스크 여러 개가 동시에 뜨면 마이그레이션을 별도 1회성 태스크로 분리할 것)
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
