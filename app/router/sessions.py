from fastapi import APIRouter


from app.core.chat_client import RequestClient
from app.model.agent_models import (
    CreateSessionRequest,
    DeleteSessionRequest,
)
from app.config import settings
from app.utils.formatter import build_session_response


session_router = APIRouter()
service_client = RequestClient(base_url=settings.BASE_URL)


@session_router.post("/new")
async def create_session(request: CreateSessionRequest):
    CREATE_SESSION_URL = f"{settings.BASE_URL}:30080/users/{request.user_id}/apps/{request.agent_name}/users/{request.user_id}/sessions"
    payload = {"app_name": request.agent_name, "user_id": request.user_id}

    try:
        session = await service_client.post_client(CREATE_SESSION_URL, payload=payload)
        return build_session_response(
            user_id=request.user_id,
            user_uuid=request.user_uuid,
            agent_id=request.agent_id,
            agent_name=request.agent_name,
            session_id=session["id"],
            status="04",
            success_ind=True,
            message_text="세션이 생성되었습니다.",
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
            location=f"{CREATE_SESSION_URL}-failed",
        )


@session_router.post("/remove")
async def delete_session(request: DeleteSessionRequest):
    """
    해당 사용자의 특정 에이전트 특정 세션 삭제 API
    - 현재는 세션별 ADK 제공 URL을 사용하여 세션을 관리 하지만, DB 구축되면 Soft Delete 방식 추가 예정
    - 세션 삭제 성공 여부 메시지 반환
    """
    DELETE_SESSION_URL = f"{settings.BASE_URL}:30080/users/{request.user_id}/apps/{request.agent_name}/users/{request.user_id}/sessions/{request.session_id}"
    try:
        await service_client.delete_client(DELETE_SESSION_URL)
        return build_session_response(
            user_id=request.user_id,
            user_uuid=request.user_uuid,
            agent_id=request.agent_id,
            agent_name=request.agent_name,
            session_id=request.session_id,
            status="04",
            success_ind=True,
            message_text="세션이 삭제되었습니다.",
        )
    except Exception as e:
        return build_session_response(
            user_id=request.user_id,
            user_uuid=request.user_uuid,
            agent_id=request.agent_id,
            agent_name=request.agent_name,
            session_id=request.session_id,
            success_ind=False,
            status="99",
            reason=str(e),
            location=f"{DELETE_SESSION_URL}-failed",
        )
