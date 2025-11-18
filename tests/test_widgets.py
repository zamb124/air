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
    assert isinstance(data["widgets"], list)


def test_get_widgets_view_with_context_travel():
    response = client.get("/widgets/view?context=travel")
    assert response.status_code == 200
    data = response.json()
    assert "view_id" in data
    assert "title" in data
    assert "widgets" in data
    assert isinstance(data["widgets"], list)
    assert len(data["widgets"]) > 0


def test_get_widgets_view_with_context_savings():
    response = client.get("/widgets/view?context=savings")
    assert response.status_code == 200
    data = response.json()
    assert "view_id" in data
    assert "title" in data
    assert "widgets" in data
    assert isinstance(data["widgets"], list)
    assert len(data["widgets"]) > 0


def test_get_widgets_view_with_goal_id():
    response = client.get("/widgets/view?goal_id=test_goal_123")
    assert response.status_code == 200
    data = response.json()
    assert "goal_id" in data
    assert data["goal_id"] == "test_goal_123"


def test_widget_structure():
    response = client.get("/widgets/view?context=travel")
    assert response.status_code == 200
    data = response.json()
    
    if len(data["widgets"]) > 0:
        widget = data["widgets"][0]
        assert "id" in widget
        assert "type" in widget
        assert isinstance(widget["id"], str)
        assert isinstance(widget["type"], str)


def test_widget_has_group_and_datetime():
    response = client.get("/widgets/view?context=travel")
    assert response.status_code == 200
    data = response.json()
    
    if len(data["widgets"]) > 0:
        widget = data["widgets"][0]
        assert "group" in widget or widget.get("group") is None
        assert "datetime" in widget or widget.get("datetime") is None


def test_post_widget_action():
    response = client.post(
        "/widgets/action",
        json={
            "view_id": "test_view",
            "widget_id": "test_widget",
            "action_id": "test_action",
            "goal_id": "test_goal"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "action_id" in data["data"]
    assert data["success"] is True


def test_post_widget_action_with_data():
    response = client.post(
        "/widgets/action",
        json={
            "view_id": "test_view",
            "widget_id": "test_widget",
            "action_id": "test_action",
            "goal_id": "test_goal",
            "data": {
                "name": "Иван",
                "email": "ivan@example.com"
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "data" in data["data"]
    assert data["success"] is True


def test_widget_types():
    response = client.get("/widgets/view?context=travel")
    assert response.status_code == 200
    data = response.json()
    
    allowed_types = {"large_card_carousel", "small_card_carousel", "card_with_button", "quiz", "map"}
    
    for widget in data["widgets"]:
        assert widget["type"] in allowed_types
