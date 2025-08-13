import httpx, time
from fastapi import APIRouter

prometheus_router = APIRouter()


# I/O 정의에 따라 request, response 값 변동
@prometheus_router.get("/metrics/requests")
async def get_request_counts():
    PROMETHEUS_URL = "http://dev03.didim365.co:29003"
    query = 'sum by (handler, method, status) (increase(http_request_duration_seconds_count{status!=""}[15d]))'
    params = {"query": query}  # PromQL

    async with httpx.AsyncClient() as client:
        res = await client.get(f"{PROMETHEUS_URL}/api/v1/query", params=params)
        res.raise_for_status()

    result = res.json()
    data = result.get("data", {}).get("result", [])

    response = [
        {
            "handler": d["metric"].get("handler"),
            "method": d["metric"].get("method"),
            "status": d["metric"].get("status"),
            "count": d["value"][1],  # 누적 증가량
        }
        for d in data
    ]

    return response
