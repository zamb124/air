import pytest
import os
import asyncio

os.environ["TEST_DB_NAME"] = "db.test.db"

from fastapi.testclient import TestClient
from main import app
from app.db import init_db, get_db_path

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    asyncio.run(init_db())
    yield
    test_db_path = get_db_path()
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

@pytest.fixture
def client():
    return TestClient(app)
