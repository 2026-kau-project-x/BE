from fastapi import APIRouter, Depends

from app.api.v1.endpoints import health, trips, vehicles
from app.core.security import require_api_key

api_router = APIRouter()
# health 는 인증 없이 (ALB/ECS 헬스체크), 나머지는 API 키 필요 (키 미설정 시 통과)
api_router.include_router(health.router)
api_router.include_router(trips.router, dependencies=[Depends(require_api_key)])
api_router.include_router(vehicles.router, dependencies=[Depends(require_api_key)])
