from pydantic import BaseModel
from typing import Optional


class GetSessionResponse(BaseModel):
    session_id: list[str]


# ADK /run Request 메서드
class RunRequest(BaseModel):
    app_name: str
    user_id: str
    session_id: str
    message: str
    streaming: bool = False


class ChatADKRequest(BaseModel):
    appName: str
    userId: str
    sessionId: str
    newMessage: dict
    streaming: bool = True
    stateDelta: Optional[dict] = None  # 상태 델타는 선택적 필드로 추가


# Deploy
class AgentConfig(BaseModel):
    name: str
    description: str
    instruction: str
    model: str = "gemini-2.0-flash"
    template: str = "assistant_agent"
    max_tokens: int = 2000
    temperature: float = 0.7


class UserCredentials(BaseModel):
    openai_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    weather_api_key: Optional[str] = None


class DeploymentRequest(BaseModel):
    user_id: str
    agent_config: AgentConfig
    credentials: UserCredentials
    overwrite: Optional[bool] = False  # 기본은 false
