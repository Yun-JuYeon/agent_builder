from fastapi.responses import StreamingResponse
import httpx
from fastapi import APIRouter, HTTPException

from google.genai.types import Content, Part

from app.core.chat_client import AgentChatClient
from app.model.agent_models import DeploymentRequest, RunRequest, ChatADKRequest
from app.config import settings


agent_router = APIRouter()


# 사용자별 에이전트 배포 API
@agent_router.post("/deploy")
async def post_to_deploy(request: DeploymentRequest):
    """
    에이전트 배포 요청 API
    """
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
    """
    해당 사용자의 모든 에이전트 목록 조회 API
    """
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


@agent_router.delete("/user/{user_id}/agents")
async def chat_with_adk_agent(user_id: str):
    """
    해당 사용자의 모든 에이전트 삭제 API
    """
    AGENT_URL = f"http://192.168.150.200:3000/api/v1/agents/user/{user_id}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(AGENT_URL)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"ADK 요청 실패: {str(e)}")


@agent_router.delete("/user/{user_id}/agents/{agent_name}")
async def chat_with_adk_agent(user_id: str, agent_name: str):
    """
    해당 사용자의 특정 에이전트 삭제 API
    """
    AGENT_URL = f"http://192.168.150.200:3000/api/v1/agents/user/{user_id}/{agent_name}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(AGENT_URL)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"ADK 요청 실패: {str(e)}")


# Agent와의 채팅 API
@agent_router.post("/user/{user_id}/chat/{app_name}")
async def chat_agent(request: RunRequest):
    """
    ```json
    {
        "app_name": "calculator_agent",
        "user_id": "user",
        "message": "111*222는?",
        "session_id": "9b7a31e5-62dc-40b6-9223-030d214082e4",
        "streaming": true
    }
    ```
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
