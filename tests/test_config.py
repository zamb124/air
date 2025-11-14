import json
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch
from app.config import load_config, get_config_value, CONFIG_PATH, _config


def test_load_config_with_existing_file():
    test_config = {
        "gismeteo": {
            "api_token": "test_token_123"
        },
        "other": {
            "setting": "value"
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_config, f)
        temp_path = Path(f.name)
    
    try:
        with patch('app.config.CONFIG_PATH', temp_path):
            with patch('app.config._config', {}):
                config = load_config()
                assert config == test_config
                assert config["gismeteo"]["api_token"] == "test_token_123"
    finally:
        temp_path.unlink()


def test_load_config_without_file():
    with patch('app.config.CONFIG_PATH', Path("/nonexistent/config.json")):
        with patch('app.config._config', {}):
            config = load_config()
            assert config == {}


def test_get_config_value_existing_key():
    test_config = {
        "gismeteo": {
            "api_token": "test_token_123"
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_config, f)
        temp_path = Path(f.name)
    
    try:
        with patch('app.config.CONFIG_PATH', temp_path):
            with patch('app.config._config', {}):
                value = get_config_value("gismeteo.api_token")
                assert value == "test_token_123"
    finally:
        temp_path.unlink()


def test_get_config_value_nested_key():
    test_config = {
        "level1": {
            "level2": {
                "level3": "deep_value"
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_config, f)
        temp_path = Path(f.name)
    
    try:
        with patch('app.config.CONFIG_PATH', temp_path):
            with patch('app.config._config', {}):
                value = get_config_value("level1.level2.level3")
                assert value == "deep_value"
    finally:
        temp_path.unlink()


def test_get_config_value_with_default():
    test_config = {}
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_config, f)
        temp_path = Path(f.name)
    
    try:
        with patch('app.config.CONFIG_PATH', temp_path):
            with patch('app.config._config', {}):
                value = get_config_value("nonexistent.key", "default_value")
                assert value == "default_value"
    finally:
        temp_path.unlink()


def test_get_config_value_nonexistent_key():
    test_config = {
        "existing": "value"
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_config, f)
        temp_path = Path(f.name)
    
    try:
        with patch('app.config.CONFIG_PATH', temp_path):
            with patch('app.config._config', {}):
                value = get_config_value("nonexistent.key")
                assert value is None
    finally:
        temp_path.unlink()


def test_get_config_value_partial_path():
    test_config = {
        "gismeteo": {
            "api_token": "test_token"
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_config, f)
        temp_path = Path(f.name)
    
    try:
        with patch('app.config.CONFIG_PATH', temp_path):
            with patch('app.config._config', {}):
                value = get_config_value("gismeteo.nonexistent", "default")
                assert value == "default"
    finally:
        temp_path.unlink()

