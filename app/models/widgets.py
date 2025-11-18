from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel
from datetime import datetime


class WidgetMetadata(BaseModel):
    price: Optional[float] = None
    rating: Optional[float] = None
    location: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None
    marker_color: Optional[str] = None
    marker_icon: Optional[str] = None
    audio_url: Optional[str] = None
    duration: Optional[int] = None
    thumbnail_url: Optional[str] = None
    video_url: Optional[str] = None
    date: Optional[str] = None
    available: Optional[bool] = None
    events_count: Optional[int] = None
    datetime: Optional[str] = None
    status: Optional[str] = None
    current: Optional[float] = None
    total: Optional[float] = None
    percentage: Optional[float] = None
    unit: Optional[str] = None
    data: Optional[List[Dict[str, Any]]] = None
    labels: Optional[List[str]] = None
    colors: Optional[List[str]] = None
    step_number: Optional[int] = None
    completed: Optional[bool] = None
    tab_id: Optional[str] = None
    format: Optional[str] = None


class Action(BaseModel):
    id: str
    type: Literal[
        "send_message", "open_url", "navigate", "update_view",
        "submit_form", "validate_form", "show_widget"
    ]
    button_text: str
    button_style: Optional[Literal["primary", "secondary", "outline", "danger", "link"]] = "primary"
    message: Optional[str] = None
    message_template: Optional[str] = None
    url: Optional[str] = None
    target: Optional[str] = None
    validation: Optional[Dict[str, Any]] = None
    required_fields: Optional[List[str]] = None
    condition: Optional[Dict[str, Any]] = None


class Item(BaseModel):
    id: str
    primary_text: str
    secondary_text: Optional[str] = None
    tertiary_text: Optional[str] = None
    image_url: Optional[str] = None
    icon: Optional[str] = None
    badge: Optional[str] = None
    metadata: Optional[WidgetMetadata] = None
    actions: Optional[List[Action]] = None


class FormFieldValidation(BaseModel):
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min: Optional[float] = None
    max: Optional[float] = None
    pattern: Optional[str] = None
    error_message: Optional[str] = None
    all_required: Optional[bool] = None


class FormFieldOption(BaseModel):
    value: str
    label: str


class FormField(BaseModel):
    id: str
    type: Literal[
        "text", "email", "tel", "number", "date", "time", "datetime",
        "select", "multiselect", "checkbox", "radio", "textarea", "file", "password"
    ]
    label: str
    placeholder: Optional[str] = None
    required: Optional[bool] = False
    validation: Optional[FormFieldValidation] = None
    options: Optional[List[FormFieldOption]] = None
    default_value: Optional[Any] = None
    help_text: Optional[str] = None


class WidgetConfig(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    style: Optional[Dict[str, Any]] = None
    show_dots: Optional[bool] = None
    auto_play: Optional[bool] = None
    layout: Optional[Literal["compact", "spacious"]] = None
    center: Optional[Dict[str, float]] = None
    zoom: Optional[int] = None
    height: Optional[int] = None
    aspect_ratio: Optional[str] = None
    fit: Optional[Literal["cover", "contain"]] = None
    mode: Optional[Literal["single", "range"]] = None
    min_date: Optional[str] = None
    max_date: Optional[str] = None
    orientation: Optional[Literal["vertical", "horizontal"]] = None
    chart_type: Optional[Literal["line", "bar", "pie", "area"]] = None
    multiple: Optional[bool] = None
    label: Optional[str] = None
    autoplay: Optional[bool] = None
    controls: Optional[bool] = None
    submit_button_text: Optional[str] = None


class Widget(BaseModel):
    id: str
    type: Literal[
        "button", "card_carousel", "text_list", "map", "image", "audio",
        "video", "form", "calendar", "timeline", "progress", "chart",
        "accordion", "tabs", "stepper", "divider", "text"
    ]
    date: Optional[str] = None
    config: Optional[WidgetConfig] = None
    items: Optional[List[Item]] = None
    fields: Optional[List[FormField]] = None
    actions: Optional[List[Action]] = None


class TimelineDate(BaseModel):
    date: str
    label: Optional[str] = None
    widgets: List[Widget]


class Timeline(BaseModel):
    enabled: bool
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    dates: Optional[List[TimelineDate]] = None


class ViewMetadata(BaseModel):
    session_id: Optional[str] = None
    context: Optional[str] = None
    updated_at: Optional[str] = None


class ViewWidgets(BaseModel):
    before_timeline: List[Widget]
    after_timeline: List[Widget]


class WidgetViewResponse(BaseModel):
    view_id: str
    title: str
    metadata: Optional[ViewMetadata] = None
    timeline: Optional[Timeline] = None
    widgets: ViewWidgets


class WidgetActionRequest(BaseModel):
    view_id: str
    widget_id: str
    item_id: Optional[str] = None
    action_id: str
    session_id: Optional[str] = None
    form_data: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None


class WidgetActionResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

