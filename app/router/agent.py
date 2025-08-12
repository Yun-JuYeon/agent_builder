from fastapi.responses import StreamingResponse
import httpx
from fastapi import APIRouter, HTTPException

from google.genai.types import Content, Part

from app.core.chat_client import AgentChatClient
from app.model.agent_models import DeploymentRequest, RunRequest, ChatADKRequest
from app.config import settings


agent_router = APIRouter()


# # I/O 정의에 따라 request, response 값 변동
# @agent_router.post("/chat")
# async def chat_with_adk_agent(request: RunRequest):
#     CHAT_AGENT_URL = "http://192.168.150.200:3000/api/v1/test-chat/jyyun/message"
#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.post(CHAT_AGENT_URL, json=request.model_dump())
#             response.raise_for_status()
#             return response.json()
#         except httpx.HTTPError as e:
#             raise HTTPException(status_code=500, detail=f"ADK 요청 실패: {str(e)}")


# @agent_router.get("/agent-info")
# async def agent_info():
#     """Provide agent information"""
#     return {
#         "agent_name": root_agent.name,
#         "description": root_agent.description,
#         "model": root_agent.model,
#         "tools": [t.__name__ for t in root_agent.tools],
#     }


# @agent_router.post("/weather-chat")
# async def chat(req: RunRequest):
#     msg = req.message.lower().strip()

#     if "경보" in msg:
#         result = await mcp.call_tool("get_alerts", {"state": "CA"})
#     elif "날씨" in msg or "예보" in msg:
#         result = await mcp.call_tool(
#             "get_forecast", {"latitude": 37.7749, "longitude": -122.4194}
#         )
#     else:
#         result = "죄송해요, 이해하지 못했어요."

#     return {"response": result}


# 사용자별 에이전트 배포 API
@agent_router.post("/deploy")
async def post_to_deploy(request: DeploymentRequest):
    DEPLOY_URL = "http://192.168.150.200:3000/api/v1/agents/deploy"
    OVERWRITE_DEPLOY_URL = "http://192.168.150.200:3000/api/v1/agents/deploy/overwrite"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(DEPLOY_URL, json=request.model_dump())
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            # 409 Conflict 발생 시(동일 이름 요청)
            if e.response.status_code == 409:
                # 2차 시도: update 경로로 재요청
                try:
                    update_response = await client.post(
                        OVERWRITE_DEPLOY_URL, json=request.model_dump()
                    )
                    update_response.raise_for_status()
                    return update_response.json()
                except httpx.HTTPStatusError as ue:
                    raise HTTPException(
                        status_code=ue.response.status_code,
                        detail=f"overwrite 경로 실패: {ue.response.text}",
                    )

            # 다른 에러는 그대로 전달
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"deploy 요청 실패: {e.response.text}",
            )


# 사용자별 에이전트 목록 조회 API
@agent_router.get("/user/{user_id}/agents")
async def get_user_agents(user_id: str):
    REQUEST_URL = f"http://192.168.150.200:3000/api/v1/agents/user/{user_id}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(REQUEST_URL)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"api/v1/agents/user/{user_id} 요청 실패: {e.response.text}",
            )


# Agent와의 채팅 API
@agent_router.post("/user/{user_id}/chat/{app_name}")
async def chat_agent(request: RunRequest):
    """
    {
        "app_name": "calculator_agent",
        "user_id": "user",
        "message": "111*222는?",
        "session_id": "9b7a31e5-62dc-40b6-9223-030d214082e4",
        "streaming": true
    }
    """
    port = "8006"  # 사용자별 포트 조회 하는 로직 필요
    base_url = settings.BASE_URL
    user_content = Content(parts=[Part(text=request.message)], role="user")

    service = AgentChatClient(base_url)

    chat_adk_request = ChatADKRequest(
        appName=request.app_name,
        userId=request.user_id,
        sessionId=request.session_id,
        newMessage=user_content.model_dump(),
        streaming=request.streaming,
    )

    return StreamingResponse(
        service.stream_chat(port, chat_adk_request.model_dump()),
        media_type="text/event-stream",
    )
