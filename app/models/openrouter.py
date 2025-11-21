from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any, Literal


class ChatMessage(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    name: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None


class ChatCompletionRequest(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    n: Optional[int] = None
    stream: Optional[bool] = None
    stop: Optional[List[str]] = None
    max_tokens: Optional[int] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    logit_bias: Optional[Dict[str, float]] = None
    user: Optional[str] = None
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[Any] = None


class ChatCompletionChoice(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    index: int
    message: ChatMessage
    finish_reason: Optional[str] = None


class Usage(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None


class ChatCompletionResponse(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    id: str
    object: str
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: Optional[Usage] = None


class ModelInfo(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    id: str
    name: Optional[str] = None
    object: Optional[str] = None
    created: Optional[int] = None
    owned_by: Optional[str] = None
    permission: Optional[List[Dict[str, Any]]] = None
    root: Optional[str] = None
    parent: Optional[str] = None
    canonical_slug: Optional[str] = None
    description: Optional[str] = None
    context_length: Optional[int] = None
    architecture: Optional[Dict[str, Any]] = None
    pricing: Optional[Dict[str, Any]] = None
    top_provider: Optional[Dict[str, Any]] = None


class ModelsListResponse(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    object: Optional[str] = None
    data: List[ModelInfo]

