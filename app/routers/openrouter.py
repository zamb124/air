from fastapi import APIRouter, Request, HTTPException
from typing import Dict, Any
import logging
from app.services.openrouter import proxy_request
from app.models.openrouter import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ModelsListResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/openrouter", tags=["openrouter"])


@router.post(
    "/chat/completions",
    response_model=ChatCompletionResponse,
    summary="Chat Completions",
    description="Создает completion для списка сообщений чата. Проксирует запрос в OpenRouter API."
)
async def chat_completions(request: ChatCompletionRequest):
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
    description="Получает список доступных моделей. Проксирует запрос в OpenRouter API."
)
async def list_models():
    try:
        result = await proxy_request("GET", "models")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error proxying request to OpenRouter: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{path:path}")
async def proxy_any_post(path: str, request: Request):
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
async def proxy_any_get(path: str, request: Request):
    try:
        params = dict(request.query_params)
        result = await proxy_request("GET", path, params=params)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error proxying request to OpenRouter: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

