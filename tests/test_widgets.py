import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_get_widgets_view():
    response = client.get("/widgets/view")
    assert response.status_code == 200
    data = response.json()
    assert "view_id" in data
    assert "title" in data
    assert "widgets" in data
    assert isinstance(data["view_id"], str)
    assert isinstance(data["title"], str)


def test_get_widgets_view_with_context_travel():
    response = client.get("/widgets/view?context=travel")
    assert response.status_code == 200
    data = response.json()
    assert "view_id" in data
    assert "title" in data
    assert "timeline" in data
    assert "widgets" in data
    assert data["timeline"]["enabled"] is True
    assert "before_timeline" in data["widgets"]
    assert "after_timeline" in data["widgets"]
    assert isinstance(data["widgets"]["before_timeline"], list)
    assert isinstance(data["widgets"]["after_timeline"], list)


def test_get_widgets_view_with_context_savings():
    response = client.get("/widgets/view?context=savings")
    assert response.status_code == 200
    data = response.json()
    assert "view_id" in data
    assert "title" in data
    assert "widgets" in data
    assert "before_timeline" in data["widgets"]
    assert isinstance(data["widgets"]["before_timeline"], list)
    assert len(data["widgets"]["before_timeline"]) > 0


def test_get_widgets_view_with_session_id():
    response = client.get("/widgets/view?session_id=test_session_123")
    assert response.status_code == 200
    data = response.json()
    assert "metadata" in data
    if data["metadata"]:
        assert data["metadata"]["session_id"] == "test_session_123"


def test_widget_structure():
    response = client.get("/widgets/view?context=travel")
    assert response.status_code == 200
    data = response.json()
    
    if len(data["widgets"]["before_timeline"]) > 0:
        widget = data["widgets"]["before_timeline"][0]
        assert "id" in widget
        assert "type" in widget
        assert isinstance(widget["id"], str)
        assert isinstance(widget["type"], str)


def test_widget_has_date_field():
    response = client.get("/widgets/view?context=travel")
    assert response.status_code == 200
    data = response.json()
    
    if len(data["widgets"]["before_timeline"]) > 0:
        widget = data["widgets"]["before_timeline"][0]
        assert "date" in widget


def test_post_widget_action():
    response = client.post(
        "/widgets/action",
        json={
            "view_id": "test_view",
            "widget_id": "test_widget",
            "action_id": "test_action",
            "session_id": "test_session"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "action_id" in data["data"]
    assert data["success"] is True


def test_post_widget_action_with_form_data():
    response = client.post(
        "/widgets/action",
        json={
            "view_id": "test_view",
            "widget_id": "test_widget",
            "action_id": "test_action",
            "session_id": "test_session",
            "form_data": {
                "name": "Иван",
                "email": "ivan@example.com"
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "form_data" in data["data"]
    assert data["success"] is True

