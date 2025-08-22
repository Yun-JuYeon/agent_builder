import uuid
from pydantic import BaseModel
from typing import Optional

# === 공통 스키마===
class ResponseMessage(BaseModel):
    code: str = ""
    text: str = ""


class ResponseReason(BaseModel):
    text: str = ""
    location: str = ""


class AgentResponseResult(BaseModel):  ### 기본값 사용
    success_ind: bool = True
    status: str = "04"  # 04: 성공
    message: ResponseMessage = ResponseMessage()
    reason: ResponseReason = ResponseReason()


class AgentResponseData(BaseModel):
    user_id: str
    user_uuid: uuid.UUID
    agent_id: uuid.UUID
    agent_name: str
    session_id: Optional[uuid.UUID] = None
    message_text: Optional[str] = None
    message_mime_type: Optional[str] = None



# create session
class CreateSessionRequest(BaseModel):
    user_id: str
    user_uuid: uuid.UUID
    agent_id: uuid.UUID
    agent_name: str


class CreateSessionResponse(BaseModel):
    response: AgentResponseData
    result: AgentResponseResult


# delete session
class DeleteSessionRequest(BaseModel):
    user_id: str
    user_uuid: uuid.UUID
    agent_id: uuid.UUID
    agent_name: str
    session_id: uuid.UUID



# Deploy
class AgentConfig(BaseModel):
    name: str
    description: str
    instruction: str
    model: str = "gemini-2.0-flash"
    template: str = "single_node_agent"
    max_tokens: int = 2000
    temperature: float = 0.7
    tools: list[uuid.UUID] = []


class UserCredentials(BaseModel):
    openai_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    weather_api_key: Optional[str] = None


class DeploymentRequest(BaseModel):
    user_id: str
    agent_config: AgentConfig
    user_credentials: UserCredentials
    overwrite: Optional[bool] = False  # 기본은 false


# UI to AP Deploy
class UIDeploySchDetail(BaseModel):
    agent_sch_exec_cycle: str = "01"  # 01: 즉시배포
    agent_sch_exect_week: list[str]
    agent_sch_exec_month: list[str]
    agent_sch_exec_time: str
    agent_sch_init_message: str


class UIDeployRequest(BaseModel):
    user_id: str
    user_uuid: uuid.UUID
    agent_id: uuid.UUID
    agent_name: str
    mcp_id: list[uuid.UUID]
    agent_instruction_message: str
    agent_sch_type: str = "01"  # 01: 즉시배포
    agent_sch_detail: UIDeploySchDetail


class AgentDeployResponseData(BaseModel):
    user_id: str
    user_uuid: uuid.UUID
    agent_id: uuid.UUID
    agent_name: str
    mcp_id: list[uuid.UUID]
    agent_sch_type: str
    session_id: Optional[uuid.UUID] = None


class AgentDeployResponse(BaseModel):
    response: AgentDeployResponseData
    result: AgentResponseResult


class DeleteAgentRequest(BaseModel):
    user_id: str
    user_uuid: uuid.UUID
    agent_id: uuid.UUID
    agent_name: str



# ADK /run Request 메서드
class AgnetExecuteAttachedFiles(BaseModel):
    attached_file_id: uuid.UUID
    attached_file_seq: int
    attached_files_count: int


class AgentExecuteRequest(BaseModel):
    user_id: str
    user_uuid: uuid.UUID
    agent_id: uuid.UUID
    agent_name: str
    session_id: uuid.UUID
    prompt_text: str   # 사용자가 입력한 텍스트
    attached_files_fl: str = "N"    # 첨부파일 여부
    attached_files_list: Optional[AgnetExecuteAttachedFiles]


class AgentExecuteResponse(BaseModel):
    response: AgentResponseData
    result: AgentResponseResult


class ChatADKRequest(BaseModel):
    appName: str
    userId: str
    sessionId: str
    newMessage: dict
    streaming: bool = True
    stateDelta: Optional[dict] = None  # 상태 델타는 선택적 필드로 추가
