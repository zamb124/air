from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime, timedelta
from app.models.widgets import (
    WidgetViewResponse, WidgetActionRequest, WidgetActionResponse,
    Widget, Item, Action, QuizQuestion, QuizOption
)

router = APIRouter(prefix="/widgets", tags=["widgets"])


@router.get("/view", response_model=WidgetViewResponse)
async def get_widgets_view(
    session_id: Optional[str] = Query(None, description="Идентификатор сессии"),
    context: Optional[str] = Query(None, description="Контекст использования")
):
    if context == "travel":
        return _get_travel_view(session_id, context)
    elif context == "savings":
        return _get_savings_view(session_id, context)
    else:
        return _get_default_view(session_id, context or "default")


def _get_travel_view(session_id: Optional[str], context: str) -> WidgetViewResponse:
    today = datetime.now()
    date_1 = today.strftime("%Y-%m-%d")
    date_2 = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    date_3 = (today + timedelta(days=2)).strftime("%Y-%m-%d")
    
    datetime_1 = f"{date_1}T10:00:00"
    datetime_2 = f"{date_1}T11:00:00"
    datetime_3 = f"{date_2}T10:00:00"
    datetime_4 = f"{date_3}T10:00:00"

    widgets = [
        Widget(
            id="widget_flights",
            type="large_card_carousel",
            title="Выберите авиабилеты",
            group="Подготовка",
            group_order=1,
            datetime=datetime_1,
            order=1,
            items=[
                Item(
                    id="flight_1",
                    text="SU 123 Москва → Сочи",
                    subtitle="15 янв, 10:00, от 5 000 руб",
                    icon="✈️",
                    metadata={"price": 5000},
                    actions=[
                        Action(
                            id="action_select_flight_1",
                            type="send_message",
                            button_text="Выбрать",
                            message="Выбрать рейс SU 123 Москва-Сочи на 15 янв 10:00 за 5000 руб"
                        )
                    ]
                ),
                Item(
                    id="flight_2",
                    text="DP 456 Москва → Сочи",
                    subtitle="15 янв, 14:30, от 4 500 руб",
                    icon="✈️",
                    metadata={"price": 4500},
                    actions=[
                        Action(
                            id="action_select_flight_2",
                            type="send_message",
                            button_text="Выбрать",
                            message="Выбрать рейс DP 456 Москва-Сочи на 15 янв 14:30 за 4500 руб"
                        )
                    ]
                )
            ]
        ),
        Widget(
            id="widget_hotel_day1",
            type="card_with_button",
            title="Ваш отель",
            group=date_1,
            group_order=2,
            datetime=datetime_2,
            order=1,
            items=[
                Item(
                    id="hotel_1",
                    text="Corinthia",
                    subtitle="Заселение в 11:00, 7 декабря. Выселение до 9:00, 9 декабря",
                    image_url="https://example.com/hotel1.jpg",
                    metadata={"address": "г. Санкт-Петербург, Невский пр-т, д. 57"}
                )
            ],
            actions=[
                Action(
                    id="action_open_map",
                    type="open_url",
                    button_text="Открыть на карте",
                    url="https://maps.yandex.ru/..."
                )
            ]
        ),
        Widget(
            id="widget_restaurants_day1",
            type="small_card_carousel",
            title="Завтрак в ресторане",
            group=date_1,
            group_order=2,
            datetime=datetime_2,
            order=2,
            items=[
                Item(
                    id="restaurant_1",
                    text="Mad Espresso",
                    image_url="https://example.com/rest1.jpg",
                    actions=[
                        Action(
                            id="action_restaurant_1",
                            type="send_message",
                            button_text="Выбрать",
                            message="Показать детали ресторана Mad Espresso"
                        )
                    ]
                ),
                Item(
                    id="restaurant_2",
                    text="Animals",
                    image_url="https://example.com/rest2.jpg",
                    actions=[
                        Action(
                            id="action_restaurant_2",
                            type="send_message",
                            button_text="Выбрать",
                            message="Показать детали ресторана Animals"
                        )
                    ]
                ),
                Item(
                    id="restaurant_3",
                    text="Aster",
                    image_url="https://example.com/rest3.jpg",
                    actions=[
                        Action(
                            id="action_restaurant_3",
                            type="send_message",
                            button_text="Выбрать",
                            message="Что лучше попробовать в Aster в Питер на завтрак"
                        )
                    ]
                )
            ]
        ),
        Widget(
            id="widget_map_hotel",
            type="map",
            title="Карта отелей",
            group=date_1,
            group_order=2,
            datetime=datetime_2,
            order=3,
            data={
                "center": {"lat": 55.7522, "lon": 37.6156},
                "zoom": 13,
                "markers": [
                    {"lat": 55.7522, "lon": 37.6156, "title": "Corinthia"}
                ]
            }
        ),
        Widget(
            id="widget_guides_day2",
            type="small_card_carousel",
            title="Выберите гида",
            group=date_2,
            group_order=3,
            datetime=datetime_3,
            order=1,
            items=[
                Item(
                    id="guide_1",
                    text="Иван Иванов",
                    subtitle="Экскурсии по Москве",
                    image_url="https://example.com/guide1.jpg",
                    icon="👨‍🏫",
                    metadata={"rating": 4.8},
                    actions=[
                        Action(
                            id="action_select_guide_1",
                            type="send_message",
                            button_text="Забронировать",
                            message="Забронировать гида Иван Иванов"
                        )
                    ]
                ),
                Item(
                    id="guide_2",
                    text="Мария Петрова",
                    subtitle="Экскурсии по Красной площади",
                    image_url="https://example.com/guide2.jpg",
                    icon="👩‍🏫",
                    metadata={"rating": 4.6},
                    actions=[
                        Action(
                            id="action_select_guide_2",
                            type="send_message",
                            button_text="Забронировать",
                            message="Забронировать гида Мария Петрова"
                        )
                    ]
                )
            ]
        )
    ]

    return WidgetViewResponse(
        view_id="travel_view_123",
        title="Поездка в Питер",
        session_id=session_id,
        context=context,
        widgets=widgets
    )


def _get_savings_view(session_id: Optional[str], context: str) -> WidgetViewResponse:
    today = datetime.now()
    datetime_1 = f"{today.strftime('%Y-%m-%d')}T10:00:00"
    datetime_2 = f"{today.strftime('%Y-%m-%d')}T11:00:00"

    widgets = [
        Widget(
            id="widget_car_selection",
            type="large_card_carousel",
            title="Машины на выбор",
            group="Выбор машины",
            group_order=1,
            datetime=datetime_1,
            order=1,
            items=[
                Item(
                    id="car_1",
                    text="Geely Xingyuan",
                    subtitle="субкомпактный электромобиль-хетчбэк, разработанный китайской компанией Geely Auto",
                    image_url="https://example.com/car1.jpg",
                    metadata={"price": 6500000},
                    actions=[
                        Action(
                            id="action_calculate_cost",
                            type="send_message",
                            button_text="Рассчитать стоимость",
                            message="Рассчитать стоимость машины Geely Xingyuan"
                        )
                    ]
                )
            ]
        ),
        Widget(
            id="widget_savings_steps",
            type="small_card_carousel",
            title="Этапы накопления",
            group="План накопления",
            group_order=2,
            datetime=datetime_2,
            order=1,
            items=[
                Item(
                    id="step_1",
                    text="Открыть счёт накопления",
                    icon="💰",
                    image_url="https://example.com/step1.jpg",
                    actions=[
                        Action(
                            id="action_step_1",
                            type="send_message",
                            button_text="Открыть",
                            message="Открыть счёт накопления"
                        )
                    ]
                ),
                Item(
                    id="step_2",
                    text="Сколько с ЗП откладывать",
                    icon="💰",
                    image_url="https://example.com/step2.jpg",
                    actions=[
                        Action(
                            id="action_step_2",
                            type="send_message",
                            button_text="Рассчитать",
                            message="Помоги расчитать сколько мне надо откладывать с моей зарплаты денег, чтобы копить на машину"
                        )
                    ]
                ),
                Item(
                    id="step_3",
                    text="Внести залог за машину",
                    icon="💰",
                    image_url="https://example.com/step3.jpg",
                    actions=[
                        Action(
                            id="action_step_3",
                            type="send_message",
                            button_text="Внести",
                            message="Внести залог за машину"
                        )
                    ]
                )
            ]
        ),
        Widget(
            id="widget_progress",
            type="card_with_button",
            title="Прогресс накопления",
            group="План накопления",
            group_order=2,
            datetime=datetime_2,
            order=2,
            items=[
                Item(
                    id="progress_1",
                    text="Накоплено 1 500 000 из 3 000 000 руб",
                    subtitle="50% завершено",
                    metadata={"current": 1500000, "total": 3000000, "percentage": 50}
                )
            ],
            actions=[
                Action(
                    id="action_show_details",
                    type="send_message",
                    button_text="Подробнее",
                    message="Показать детали накопления"
                )
            ]
        )
    ]

    return WidgetViewResponse(
        view_id="savings_view_123",
        title="Покупка китайской машины",
        session_id=session_id,
        context=context,
        widgets=widgets
    )


def _get_default_view(session_id: Optional[str], context: str) -> WidgetViewResponse:
    today = datetime.now()
    datetime_1 = f"{today.strftime('%Y-%m-%d')}T10:00:00"

    widgets = [
        Widget(
            id="widget_ai_basics",
            type="card_with_button",
            title="Типы ИИ помощников",
            group="Основы ИИ",
            group_order=1,
            datetime=datetime_1,
            order=1,
            items=[
                Item(
                    id="content_1",
                    text="Узкий искусственный интеллект (Narrow AI)",
                    subtitle="Описание: Узкий ИИ предназначен для выполнения ограниченного набора задач..."
                )
            ],
            actions=[
                Action(
                    id="action_start_quiz",
                    type="send_message",
                    button_text="Пройти квиз",
                    message="Показать квиз по основам ИИ"
                )
            ]
        ),
        Widget(
            id="widget_quiz",
            type="quiz",
            title="Первый квиз",
            group="Первый квиз",
            group_order=2,
            datetime=datetime_1,
            order=1,
            questions=[
                QuizQuestion(
                    id="question_1",
                    text="Какой тип ИИ представлен голосовым помощником?",
                    options=[
                        QuizOption(id="opt_1", text="Реактивный ИИ (Reactive AI)", is_correct=False),
                        QuizOption(id="opt_2", text="Общий ИИ (General AI)", is_correct=False),
                        QuizOption(id="opt_3", text="Узкий ИИ (Narrow AI)", is_correct=True),
                        QuizOption(id="opt_4", text="Искусственный Суперинтеллект", is_correct=False)
                    ]
                )
            ]
        )
    ]

    return WidgetViewResponse(
        view_id="default_view_123",
        title="Обучение ИИ",
        session_id=session_id,
        context=context,
        widgets=widgets
    )


@router.post("/action", response_model=WidgetActionResponse)
async def execute_widget_action(action_request: WidgetActionRequest):
    return WidgetActionResponse(
        success=True,
        message=f"Действие {action_request.action_id} выполнено",
        data={"action_id": action_request.action_id, "data": action_request.data}
    )
