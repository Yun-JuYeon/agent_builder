from pydantic import BaseModel, Field
from typing import Any, Optional, List
from google.genai import types

class AgentRunRequest(BaseModel):
  app_name: str
  user_id: str
  session_id: str
  new_message: types.Content
  streaming: bool = False
  state_delta: Optional[dict[str, Any]] = None


class GetEventGraphResult(BaseModel):
  dot_src: str

