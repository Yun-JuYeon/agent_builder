import re

from typing import Optional
from app.model.agent_models import (
    AgentResponseData,
    AgentExecuteResponse,
    AgentResponseResult,
    CreateSessionResponse,
    ResponseMessage,
    ResponseReason,
)


def sanitize_agent_name(name: str) -> str:
    # 1. 공백을 언더스코어로 변환
    name = name.replace(" ", "_")
    # 2. 한글(완성형+자모), 영문, 숫자, 언더스코어만 남기기
    re_name = re.sub(r"[^가-힣ㄱ-ㅎㅏ-ㅣa-zA-Z0-9_]", "", name)
    return re_name or "default_agent"


# ===== 공통 유틸 =====


def build_response_data(
    user_id,
    user_uuid,
    agent_id,
    agent_name,
    session_id=None,
    message_text=None,
    message_mime_type=None,
):
    return AgentResponseData(
        user_id=user_id,
        user_uuid=user_uuid,
        agent_name=agent_name,
        agent_id=agent_id,
        session_id=session_id,
        message_text=message_text,
        message_mime_type=message_mime_type,
    )


def build_result(
    agent_id,
    success_ind,
    status,
    message_text: str = "",
    reason: str = "",
    location: str = "",
):
    return AgentResponseResult(
        success_ind=success_ind,
        status=status,
        message=ResponseMessage(
            code=f"AGENT-{agent_id}", text=message_text
        ),
        reason=ResponseReason(text=reason, location=location),
    )


# ===== 세션 응답 =====
def build_session_response(
    user_id,
    user_uuid,
    agent_id,
    agent_name,
    session_id=None,
    success_ind=True,
    status="00",
    message_text="",
    reason="",
    location="",
):
    response = build_response_data(user_id, user_uuid, agent_id, agent_name, session_id)
    result = build_result(
        agent_id=agent_id,
        success_ind=success_ind,
        status=status,
        message_text=message_text,
        reason=reason,
        location=location,
    )
    return CreateSessionResponse(response=response, result=result).model_dump(
        exclude_none=True
    )


# ===== 채팅 =====
def build_metadata(
    user_id,
    user_uuid,
    agent_id,
    agent_name,
    session_id=None,
    success_ind=True,
    status="00",
    message="",
    mime_type="text/markdown",
    reason="",
    location="",
):
    """SSE 이벤트용 metadata payload"""
    response = build_response_data(
        user_id, user_uuid, agent_id, agent_name, session_id, message, mime_type
    )
    result = build_result(
        agent_id=agent_id,
        success_ind=success_ind,
        status=status,
        message_text="실행이 완료되었습니다.",
        reason=reason,
        location=location,
    )
    return AgentExecuteResponse(response=response, result=result).model_dump(
        exclude_none=True
    )
