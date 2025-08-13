from fastapi import FastAPI, APIRouter
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_fastapi_instrumentator.metrics import (
    latency, requests
)
from app.router.agent import agent_router
from app.router.prometheus import prometheus_router
from app.config import settings
 
app = FastAPI()
api_router = APIRouter(prefix=settings.API_V1_STR)

Instrumentator(
    should_group_status_codes=False
).add(latency()).add(requests()).instrument(app).expose(app)

api_router.include_router(agent_router, prefix="/agent", tags=["Agent"])
api_router.include_router(prometheus_router, prefix="/prometheus", tags=["Prometheus"])

app.include_router(api_router)

@app.get("/")
def read_root():
    return {"message": "OK"}
