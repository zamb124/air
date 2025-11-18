from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel


class Action(BaseModel):
    id: str
    type: Literal["send_message", "open_url"]
    button_text: str
    message: Optional[str] = None
    url: Optional[str] = None


class Item(BaseModel):
    id: str
    text: str
    subtitle: Optional[str] = None
    image_url: Optional[str] = None
    icon: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    actions: Optional[List[Action]] = None


class QuizOption(BaseModel):
    id: str
    text: str
    is_correct: Optional[bool] = None


class QuizQuestion(BaseModel):
    id: str
    text: str
    options: List[QuizOption]


class Widget(BaseModel):
    id: str
    type: Literal["large_card_carousel", "small_card_carousel", "card_with_button", "quiz", "map"]
    title: Optional[str] = None
    group: Optional[str] = None
    group_order: Optional[int] = None
    datetime: Optional[str] = None
    order: Optional[int] = None
    items: Optional[List[Item]] = None
    questions: Optional[List[QuizQuestion]] = None
    data: Optional[Dict[str, Any]] = None
    actions: Optional[List[Action]] = None


class WidgetViewResponse(BaseModel):
    view_id: str
    title: str
    session_id: Optional[str] = None
    context: Optional[str] = None
    widgets: List[Widget]


class WidgetActionRequest(BaseModel):
    view_id: str
    widget_id: str
    item_id: Optional[str] = None
    action_id: str
    session_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class WidgetActionResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
