import asyncio
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather")

NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-korean-agent/1.0"

async def make_nws_request(url: str) -> dict | None:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[ERROR] 요청 실패: {e}")
            return None

def format_alert(feature: dict) -> str:
    props = feature["properties"]
    return f"""
🌀 이벤트: {props.get('event', '알 수 없음')}
📍 지역: {props.get('areaDesc', '알 수 없음')}
⚠️ 심각도: {props.get('severity', '정보 없음')}
📝 설명: {props.get('description', '설명이 없습니다.')}
📢 지침: {props.get('instruction', '특별한 지침이 없습니다.')}
"""

@mcp.tool()
async def get_alerts(state: str) -> str:
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "경보를 가져올 수 없습니다."

    if not data["features"]:
        return "현재 활성화된 경보가 없습니다."

    alerts = [format_alert(feature) for feature in data["features"][:3]]
    return "\n---\n".join(alerts)

@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        return "해당 위치의 예보 데이터를 가져올 수 없습니다."

    forecast_url = points_data["properties"].get("forecast")
    if not forecast_url:
        return "예보 URL을 찾을 수 없습니다."

    forecast_data = await make_nws_request(forecast_url)
    if not forecast_data:
        return "상세 예보를 가져오지 못했습니다."

    periods = forecast_data["properties"]["periods"][:3]
    result = []
    for p in periods:
        result.append(
            f"⏰ {p['name']} - 🌡️ {p['temperature']}°{p['temperatureUnit']} / ☁️ {p['shortForecast']}"
        )
    return "\n".join(result)

async def main_loop():
    print("=== MCP 날씨 콘솔 시작 ===")
    print("종료하려면 Ctrl+C 또는 Ctrl+D 누르세요.")
    while True:
        try:
            text = input("> ").strip()
            if not text:
                continue

            if "경보" in text:
                # 메시지에서 주(state) 추출 가능하면 넣으세요. 임시 고정 'CA'
                result = await mcp.call_tool("get_alerts", {"state": "CA"})
            elif "날씨" in text or "예보" in text:
                # 임시 좌표: 샌프란시스코
                result = await mcp.call_tool("get_forecast", {"latitude": 37.7749, "longitude": -122.4194})
            else:
                result = "죄송해요, 이해하지 못했어요."

            print(result)
        except (KeyboardInterrupt, EOFError):
            print("\n종료합니다.")
            break

if __name__ == "__main__":
    asyncio.run(main_loop())
