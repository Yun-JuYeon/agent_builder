import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
import requests


def get_weather(city: str) -> dict:
    """도시의 현재 날씨 정보를 가져옵니다."""
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": "뉴욕의 날씨는 맑고 기온은 25°C입니다."
        }
    return {
        "status": "error",
        "error_message": f"'{city}'의 날씨 정보는 현재 제공되지 않습니다."
    }


def get_current_time(city: str) -> dict:
    """도시의 현재 시간을 가져옵니다."""
    city_timezones = {
        "new york": "America/New_York",
        "london": "Europe/London",
        "tokyo": "Asia/Tokyo",
        "paris": "Europe/Paris"
    }
    if city.lower() in city_timezones:
        try:
            tz = ZoneInfo(city_timezones[city.lower()])
            now = datetime.datetime.now(tz)
            return {
                "status": "success",
                "report": f"{city}의 현재 시각은 {now.strftime('%Y-%m-%d %H:%M:%S %Z')}입니다."
            }
        except Exception:
            pass
    return {
        "status": "error",
        "error_message": f"'{city}'의 시간 정보는 현재 제공되지 않습니다."
    }


def web_search(query: str) -> dict:
    """간단한 웹 검색 (DuckDuckGo API 사용 예시)"""
    try:
        resp = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_redirect": 1, "no_html": 1},
            timeout=5
        )
        data = resp.json()
        if data.get("AbstractText"):
            return {
                "status": "success",
                "report": f"검색 결과: {data['AbstractText']}"
            }
        else:
            return {
                "status": "success",
                "report": f"'{query}'에 대한 구체적인 설명을 찾지 못했습니다."
            }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"웹 검색 중 오류 발생: {str(e)}"
        }


# ADK 에이전트 정의
root_agent = Agent(
    name="root_agent",
    model="gemini-2.0-flash",  # Gemini 모델
    description="도시의 시간, 날씨, 웹 검색 정보를 알려주는 한국어 에이전트",
    instruction=(
"""
당신은 사용자의 질문에 답하기 위해 다음의 2단계 프로세스를 엄격하게 따라야 합니다.

### 1단계: 툴 호출
1.  사용자의 질문을 분석하여 가장 적절한 툴을 선택하고 호출합니다.
2.  툴 호출을 완료하고, 호출 결과를 기다립니다.

### 2단계: 최종 응답 생성 및 종료
1.  툴 호출 결과가 사용자로부터 도착하면, 그 결과를 바탕으로 최종 응답을 생성하는 데 집중합니다.
2.  **이 단계에서는 절대로 툴을 다시 호출해서는 안 됩니다.**
3.  최종 응답을 자연스러운 한국어 문장으로 작성하고, 대화를 종료합니다.

만약 사용자의 질문에 맞는 툴이 없거나 툴 사용에 실패했을 경우에만, 툴 호출 없이 일반적인 대화로 응답합니다.

- get_weather(city: str): 특정 도시의 현재 날씨를 가져옵니다.
- get_current_time(city: str): 특정 도시의 현재 시간을 가져옵니다.
- web_search(query: str): 웹을 검색하여 정보를 가져옵니다.
"""
    ),
    tools=[get_weather, get_current_time, web_search],
)
