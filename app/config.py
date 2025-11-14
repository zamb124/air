import json
import os
from pathlib import Path
from typing import Dict, Any

CONFIG_PATH = Path(__file__).parent.parent / "config.json"

_config: Dict[str, Any] = {}


def load_config() -> Dict[str, Any]:
    global _config
    if not _config:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                _config = json.load(f)
        else:
            _config = {}
    return _config


def get_config_value(key_path: str, default: Any = None) -> Any:
    config = load_config()
    keys = key_path.split(".")
    value = config
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
            if value is None:
                return default
        else:
            return default
    return value if value is not None else default

