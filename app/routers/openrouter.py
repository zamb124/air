from fastapi import APIRouter, Request, HTTPException, Header
from typing import Dict, Any, Optional
import logging
from app.services.openrouter import proxy_request
from app.config import get_config_value
from app.models.openrouter import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ModelsListResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/openrouter", tags=["openrouter"])


def _get_api_token() -> str:
    return get_config_value("openrouter.api_token", "")


def _verify_token(x_api_token: Optional[str] = Header(None, alias="X-API-Token")) -> str:
    expected_token = _get_api_token()
    if not expected_token:
        raise HTTPException(status_code=500, detail="API token not configured")
    
    if not x_api_token:
        raise HTTPException(status_code=401, detail="Missing X-API-Token header")
    
    if x_api_token != expected_token:
        raise HTTPException(status_code=403, detail="Invalid API token")
    
    return x_api_token


@router.post(
    "/chat/completions",
    response_model=ChatCompletionResponse,
    summary="Chat Completions",
    description="Создает completion для списка сообщений чата. Проксирует запрос в OpenRouter API. Требует заголовок X-API-Token."
)
async def chat_completions(request: ChatCompletionRequest, token: str = Header(..., alias="X-API-Token", description="API токен для доступа")):
    _verify_token(token)
    try:
        result = await proxy_request("POST", "chat/completions", data=request.model_dump(exclude_none=True))
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error proxying request to OpenRouter: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/models",
    response_model=ModelsListResponse,
    summary="List Models",
    description="Получает список доступных моделей. Проксирует запрос в OpenRouter API. Требует заголовок X-API-Token."
)
async def list_models(token: str = Header(..., alias="X-API-Token", description="API токен для доступа")):
    _verify_token(token)
    try:
        result = await proxy_request("GET", "models")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error proxying request to OpenRouter: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{path:path}")
async def proxy_any_post(path: str, request: Request, token: str = Header(..., alias="X-API-Token", description="API токен для доступа")):
    _verify_token(token)
    try:
        body = await request.json()
        result = await proxy_request("POST", path, data=body)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error proxying request to OpenRouter: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{path:path}")
async def proxy_any_get(path: str, request: Request, token: str = Header(..., alias="X-API-Token", description="API токен для доступа")):
    _verify_token(token)
    try:
        params = dict(request.query_params)
        result = await proxy_request("GET", path, params=params)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error proxying request to OpenRouter: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

