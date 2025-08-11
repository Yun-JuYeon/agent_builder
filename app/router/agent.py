from typing import AsyncGenerator
import uuid
from fastapi.responses import StreamingResponse
import httpx
from fastapi import APIRouter, HTTPException

from google.adk.runners import Runner
from google.genai.types import Content, Part
from adk_agents.multi_tool_agent.mcp import mcp
from adk_agents.multi_tool_agent.root_agent.root_agent import root_agent
from google.adk.agents.invocation_context import RunConfig

from app.model.agent_models import DeploymentRequest, RunRequest

from app.core.db.postgres import session_service

agent_router = APIRouter()


# I/O 정의에 따라 request, response 값 변동
@agent_router.post("/chat")
async def chat_with_adk_agent(request: RunRequest):
    CHAT_AGENT_URL = "http://192.168.150.200:3000/api/v1/test-chat/jyyun/message"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(CHAT_AGENT_URL, json=request.model_dump())
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"ADK 요청 실패: {str(e)}")


# @agent_router.get("/agent-info")
# async def agent_info():
#     """Provide agent information"""
#     return {
#         "agent_name": root_agent.name,
#         "description": root_agent.description,
#         "model": root_agent.model,
#         "tools": [t.__name__ for t in root_agent.tools],
#     }


@agent_router.post("/weather-chat")
async def chat(req: RunRequest):
    msg = req.message.lower().strip()

    if "경보" in msg:
        result = await mcp.call_tool("get_alerts", {"state": "CA"})
    elif "날씨" in msg or "예보" in msg:
        result = await mcp.call_tool(
            "get_forecast", {"latitude": 37.7749, "longitude": -122.4194}
        )
    else:
        result = "죄송해요, 이해하지 못했어요."

    return {"response": result}


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
    # 1) 세션 생성/조회
    # 1. 먼저 세션 조회
    session = await session_service.get_session(
        app_name=request.app_name,
        user_id=request.user_id,
        session_id=request.session_id,
    )

    # 2. 없으면 새로 생성
    if not session:
        session = await session_service.create_session(
            app_name=request.app_name,
            user_id=request.user_id,
            session_id=request.session_id or str(uuid.uuid4()),
        )

    user_content = Content(parts=[Part(text=request.message)], role="user")

    agent = root_agent  # 프론트에서 요청할 때 agent config를 같이 주거나, app_name/user_id/session_id로 조회해서 해당 agent를 DB에서 조회해서 세팅하도록 변경 필요
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    run_config = RunConfig(
        streaming_mode="sse", response_modalities=["TEXT"], max_llm_calls=3
    )

    runner = Runner(
        agent=agent, app_name=request.app_name, session_service=session_service
    )

    async def stream_response() -> AsyncGenerator[str, None]:
        collected_output = ""

        events = runner.run_async(
            user_id=request.user_id,
            session_id=session.id,
            new_message=user_content,
            run_config=run_config,
        )

        async for event in events:
            if event.is_final_response():
                final_response = event.content.parts[0].text
                break  # 최종 응답을 받았으므로 루프 종료

            if event.content and event.content.parts:
                # 부분 응답도 스트리밍
                if text := "".join(part.text or "" for part in event.content.parts):
                    yield f"data: {text}\n\n"
                    collected_output += text

    # text/event-stream이면 SSE 방식, text/plain이면 그냥 chunk 전송
    return StreamingResponse(stream_response(), media_type="text/event-stream")
