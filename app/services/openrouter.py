import httpx
import logging
from typing import Dict, Any, Optional
from app.config import get_config_value

logger = logging.getLogger(__name__)


def _get_base_url() -> str:
    return get_config_value("openrouter.llm_base_url", "https://openrouter.ai/api/v1")


def _get_api_key() -> str:
    return get_config_value("openrouter.llm_api_key", "")


def _get_model() -> str:
    return get_config_value("openrouter.llm_model", "x-ai/grok-code-fast-1")


def _get_proxy() -> Optional[str]:
    return get_config_value("openrouter.proxy", None)


async def proxy_request(
    method: str,
    path: str,
    data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    base_url = _get_base_url()
    api_key = _get_api_key()
    proxy = _get_proxy()
    
    if not api_key:
        raise ValueError("OpenRouter API key not configured")
    
    url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    client_kwargs = {"timeout": 60.0}
    if proxy:
        client_kwargs["proxy"] = proxy
    
    async with httpx.AsyncClient(**client_kwargs) as client:
        if method.upper() == "GET":
            response = await client.get(url, headers=headers, params=params)
        elif method.upper() == "POST":
            response = await client.post(url, headers=headers, json=data, params=params)
        elif method.upper() == "PUT":
            response = await client.put(url, headers=headers, json=data, params=params)
        elif method.upper() == "DELETE":
            response = await client.delete(url, headers=headers, params=params)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        if response.status_code != 200:
            logger.error(f"OpenRouter API error: {response.status_code}, response: {response.text}")
        response.raise_for_status()
        return response.json()

