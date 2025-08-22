from fastapi.responses import StreamingResponse
import httpx
from fastapi import APIRouter, HTTPException

from google.genai.types import Content, Part

from app.core.chat_client import RequestClient
from app.model.agent_models import (
    AgentDeployResponse,
    AgentDeployResponseData,
    AgentExecuteRequest,
    AgentResponseResult,
    DeleteAgentRequest,
    DeploymentRequest,
    ResponseMessage,
    ResponseReason,
    ChatADKRequest,
    UIDeployRequest,
)
from app.config import settings
from app.utils.formatter import build_metadata, build_session_response, sanitize_agent_name
from app.utils.pattern import detect_mime_type
from app.utils.sse import sse_event


agent_router = APIRouter()
service_client = RequestClient(base_url=settings.BASE_URL)


@agent_router.post("/deploy")
async def post_to_deploy(request: UIDeployRequest):
    """
    에이전트 배포 요청 API
    """
    agent_name = sanitize_agent_name(request.agent_name)
    OVERWRITE_DEPLOY_URL = f"{settings.BASE_URL}:3001/api/v1/agents/deploy/overwrite"
    CREATE_SESSION_URL = f"{settings.BASE_URL}:30080/users/{request.user_id}/apps/{agent_name}/users/{request.user_id}/sessions"
    request_payload = DeploymentRequest(
        user_id=str(request.user_id),
        agent_config={
            "name": agent_name, 
            "description": request.agent_instruction_message,
            "instruction": request.agent_instruction_message,
            "model": "gemini-2.0-flash",
            "template": "single_node_agent",
            "max_tokens": 2000,
            "temperature": 0.7,
            "tools": request.mcp_id,  # mcp_id별로 툴 조회 후 그 이름으로 전달 하도록 수정 필요
        },
        user_credentials={
            "openai_api_key": None,  # OpenAI API 키가 필요한 경우 여기에 추가
            "google_api_key": settings.GOOGLE_API_KEY,  # Google API 키가 필요한 경우 여기에 추가
            "weather_api_key": None,  # 날씨 API 키가 필요한 경우 여기에 추가
        },
        overwrite=False,
    )

    response_data = AgentDeployResponseData(
        user_id=request.user_id,
        user_uuid=request.user_uuid,
        agent_id=request.agent_id,
        agent_name=agent_name,
        mcp_id=request.mcp_id,
        agent_sch_type=request.agent_sch_type,
    )
    try:
        response = await service_client.post_client(
            OVERWRITE_DEPLOY_URL, payload=request_payload
        )
        session_payload = {
            "app_name": agent_name,
            "user_id": str(request.user_id)
        }
        
        sessions = await service_client.post_client(url=CREATE_SESSION_URL, payload=session_payload)
        # print(sessions)
        if sessions:
            session_id = sessions["id"]
            response_data.session_id = session_id

        message = ResponseMessage(
            code=f"AGENT-{agent_name}",
            text=f"에이전트 배포가 완료되었습니다.",
        )
        result_data = AgentResponseResult(
            success_ind=True,
            status="04",
            message=message,
        )
        return_format = AgentDeployResponse(
            response=response_data, result=result_data
        ).model_dump(exclude_none=True)

        return return_format

    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code
        reason = ResponseReason(
            text=str(e), location=f"{OVERWRITE_DEPLOY_URL} - {status_code}"
        )

        message = ResponseMessage(
            code=f"AGENT-{agent_name}",
            text=f"에이전트 배포에 실패하였습니다.",
        )
        result_data = AgentResponseResult(
            success_ind=False,
            status="99",
            message=message,
            reason=reason,
        )
        return_format = AgentDeployResponse(response=response_data, result=result_data).model_dump(exclude_none=True)

        return return_format


@agent_router.post("/stop")
async def delete_agent(request: DeleteAgentRequest):
    """
    해당 사용자의 특정 에이전트 삭제 API
    """
    DELETE_AGENT_URL = f"{settings.BASE_URL}:3001/api/v1/agents/deployed/{request.user_id}/{request.agent_name}"
    try:
        await service_client.delete_client(DELETE_AGENT_URL)
        return build_session_response(
            user_id=request.user_id,
            user_uuid=request.user_uuid,
            agent_id=request.agent_id,
            agent_name=request.agent_name,
            status="08",
            success_ind=True,
            message_text="배포가 중단(삭제) 되었습니다",
        )
    except Exception as e:
        return build_session_response(
            user_id=request.user_id,
            user_uuid=request.user_uuid,
            agent_id=request.agent_id,
            agent_name=request.agent_name,
            success_ind=False,
            status="99",
            reason=str(e),
            location=f"{DELETE_AGENT_URL}-failed",
        )


@agent_router.post("/execute")
async def chat_agent(request: AgentExecuteRequest):
    """
    에이전트와 채팅하는 API
    """
    user_content = Content(parts=[Part(text=request.prompt_text)], role="user")
    adk_run_url = f"{settings.BASE_URL}:30080/users/{request.user_id}/run"

    chat_adk_request = ChatADKRequest(
        appName=str(request.agent_name),
        userId=str(request.user_id),
        sessionId=str(request.session_id),
        newMessage=user_content.model_dump(),
    )
    
    try:
        response = await service_client.post_client(
            url=adk_run_url,
            payload=chat_adk_request
        )
        message_content = response[0]['content']['parts'][0]['text']
        mime_type = detect_mime_type(message_content)
        print(f"message: {message_content}")
        print(f"mime-type: {mime_type}")
        
        return build_metadata(
            user_id=request.user_id,
            user_uuid=request.user_uuid,
            agent_id=request.agent_id,
            agent_name=request.agent_name,
            session_id=request.session_id,
            status="04",
            success_ind=True,
            message=message_content,
            mime_type=mime_type
        )
    except Exception as e:
        return build_metadata(
            user_id=request.user_id,
            user_uuid=request.user_uuid,
            agent_id=request.agent_id,
            agent_name=request.agent_name,
            success_ind=False,
            status="99",
            reason=str(e),
            location=f"{adk_run_url}-failed",
        )

    # ===== Streaming 일 경우 =====
    # async def event_generator():
    #     # 1. 시작 메타데이터
    #     yield sse_event(
    #         "metadata",
    #         build_metadata(
    #             user_id=str(request.user_id),
    #             user_uuid=str(request.user_uuid),
    #             agent_id=str(request.agent_id),
    #             session_id=str(request.session_id),
    #             status_code="05",
    #             success_ind=True,
    #             message="실행 요청되었습니다.",
    #         ),
    #     )

    #     try:
    #         # 2. 채팅 스트리밍
    #         async for chunk in service_client.stream_chat(
    #             user_id=str(request.user_id),
    #             chat_request=chat_adk_request.model_dump()
    #         ):
    #             yield f"data: {chunk}\n\n"

    #         # 3. 정상 완료 메타데이터
    #         yield sse_event(
    #             "result",
    #             build_metadata(
    #                 user_id=str(request.user_id),
    #                 user_uuid=str(request.user_uuid),
    #                 agent_id=str(request.agent_id),
    #                 session_id=str(request.session_id),
    #                 status_code="07",
    #                 success_ind=True,
    #                 message="실행 완료되었습니다.",
    #             ),
    #         )

    #     except Exception as e:
    #         # 4. 예외 발생 시 error 이벤트
    #         yield sse_event(
    #             "error",
    #             build_metadata(
    #                 user_id=str(request.user_id),
    #                 user_uuid=str(request.user_uuid),
    #                 agent_id=str(request.agent_id),
    #                 session_id=str(request.session_id),
    #                 status_code="99",
    #                 success_ind=False,
    #                 message="실행 중 오류 발생",
    #                 reason=str(e),
    #                 location="execute - stream_chat",
    #             ),
    #         )
    #         return  # <- 실패 시 바로 종료

    #     # 5. 종료 시그널
    #     yield "event: end\ndata: [DONE]\n\n"

    # return StreamingResponse(event_generator(), media_type="text/event-stream")



# @agent_router.post("/user/{user_id}/agents")
# async def post_user_agents(user_id: str):
#     """
#     해당 사용자의 모든 에이전트 목록 조회 API
#     """
#     REQUEST_URL = f"http://192.168.150.200:3000/api/v1/agents/deployed/users/{user_id}"

#     try:
#         response = await service_client.post_client(REQUEST_URL)
#         return response

#     except httpx.HTTPStatusError as e:
#         raise HTTPException(
#             status_code=e.response.status_code,
#             detail=f"api/v1/agents/user/{user_id} 요청 실패: {e.response.text}",
#         )


# @agent_router.delete("/user/{user_id}/agents")
# async def chat_with_adk_agent(user_id: str):
#     """
#     해당 사용자의 모든 에이전트 삭제 API
#     """
#     AGENT_URL = f"http://192.168.150.200:3000/api/v1/agents/user/{user_id}"
#     try:
#         response = await service_client.delete_client(AGENT_URL)
#         return response
#     except httpx.HTTPError as e:
#         raise HTTPException(status_code=500, detail=f"삭제 요청 실패: {str(e)}")


