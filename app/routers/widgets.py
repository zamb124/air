from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from datetime import datetime, timedelta
from app.models.widgets import (
    WidgetViewResponse, WidgetActionRequest, WidgetActionResponse,
    Widget, Item, Action, WidgetConfig, WidgetMetadata, FormField,
    FormFieldValidation, Timeline, TimelineDate, ViewMetadata, ViewWidgets
)

router = APIRouter(prefix="/widgets", tags=["widgets"])


@router.get("/view", response_model=WidgetViewResponse)
async def get_widgets_view(
    session_id: Optional[str] = Query(None, description="Идентификатор сессии"),
    context: Optional[str] = Query(None, description="Контекст использования")
):
    if context == "travel":
        return _get_travel_view(session_id)
    elif context == "savings":
        return _get_savings_view(session_id)
    else:
        return _get_default_view(session_id)


def _get_travel_view(session_id: Optional[str]) -> WidgetViewResponse:
    today = datetime.now()
    date_1 = today.strftime("%Y-%m-%d")
    date_2 = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    date_3 = (today + timedelta(days=2)).strftime("%Y-%m-%d")

    before_timeline = [
        Widget(
            id="widget_flights",
            type="card_carousel",
            date=date_1,
            config=WidgetConfig(
                title="Выберите авиабилеты",
                show_dots=True,
                auto_play=False
            ),
            items=[
                Item(
                    id="flight_1",
                    primary_text="SU 123 Москва → Сочи",
                    secondary_text="15 янв, 10:00",
                    tertiary_text="от 5 000 руб",
                    icon="✈️",
                    metadata=WidgetMetadata(price=5000),
                    actions=[
                        Action(
                            id="action_select_flight_1",
                            type="send_message",
                            button_text="Выбрать",
                            button_style="primary",
                            message="Выбрать рейс SU 123 Москва-Сочи на 15 янв 10:00 за 5000 руб"
                        )
                    ]
                ),
                Item(
                    id="flight_2",
                    primary_text="DP 456 Москва → Сочи",
                    secondary_text="15 янв, 14:30",
                    tertiary_text="от 4 500 руб",
                    icon="✈️",
                    metadata=WidgetMetadata(price=4500),
                    actions=[
                        Action(
                            id="action_select_flight_2",
                            type="send_message",
                            button_text="Выбрать",
                            button_style="primary",
                            message="Выбрать рейс DP 456 Москва-Сочи на 15 янв 14:30 за 4500 руб"
                        )
                    ]
                ),
                Item(
                    id="flight_3",
                    primary_text="S7 789 Москва → Сочи",
                    secondary_text="15 янв, 18:00",
                    tertiary_text="от 6 000 руб",
                    icon="✈️",
                    metadata=WidgetMetadata(price=6000),
                    actions=[
                        Action(
                            id="action_select_flight_3",
                            type="send_message",
                            button_text="Выбрать",
                            button_style="primary",
                            message="Выбрать рейс S7 789 Москва-Сочи на 15 янв 18:00 за 6000 руб"
                        )
                    ]
                )
            ]
        ),
        Widget(
            id="widget_form_booking",
            type="form",
            date=date_1,
            config=WidgetConfig(
                title="Заполните данные для бронирования",
                submit_button_text="Отправить"
            ),
            fields=[
                FormField(
                    id="name",
                    type="text",
                    label="Ваше имя",
                    placeholder="Введите имя",
                    required=True,
                    validation=FormFieldValidation(min_length=2, max_length=50)
                ),
                FormField(
                    id="email",
                    type="email",
                    label="Email",
                    placeholder="example@mail.com",
                    required=True
                ),
                FormField(
                    id="phone",
                    type="tel",
                    label="Телефон",
                    placeholder="+7 (999) 123-45-67",
                    required=True
                ),
                FormField(
                    id="date_from",
                    type="date",
                    label="Дата заезда",
                    required=True
                ),
                FormField(
                    id="date_to",
                    type="date",
                    label="Дата выезда",
                    required=True
                ),
                FormField(
                    id="guests",
                    type="number",
                    label="Количество гостей",
                    default_value=1,
                    validation=FormFieldValidation(min=1, max=10)
                )
            ],
            actions=[
                Action(
                    id="action_submit_form",
                    type="submit_form",
                    button_text="Забронировать",
                    button_style="primary",
                    message_template="Забронировать отель для {name} с {date_from} по {date_to}, гостей: {guests}, контакты: email {email}, телефон {phone}",
                    required_fields=["name", "email", "phone", "date_from", "date_to"]
                )
            ]
        )
    ]

    timeline = Timeline(
        enabled=True,
        start_date=date_1,
        end_date=date_3,
        dates=[
            TimelineDate(
                date=date_1,
                label="День 1",
                widgets=[
                    Widget(
                        id="widget_hotels_day1",
                        type="card_carousel",
                        date=date_1,
                        config=WidgetConfig(
                            title="Выберите отель на сегодня",
                            show_dots=True
                        ),
                        items=[
                            Item(
                                id="hotel_1",
                                primary_text="Отель Москва",
                                secondary_text="4 звезды, центр",
                                tertiary_text="5 000 руб/ночь",
                                image_url="https://example.com/hotel1.jpg",
                                badge="Рекомендуем",
                                metadata=WidgetMetadata(
                                    price=5000,
                                    rating=4.5,
                                    location="Москва, центр"
                                ),
                                actions=[
                                    Action(
                                        id="action_select_hotel_1",
                                        type="send_message",
                                        button_text="Выбрать",
                                        button_style="primary",
                                        message="Выбрать отель Отель Москва за 5000 руб с рейтингом 4.5"
                                    )
                                ]
                            ),
                            Item(
                                id="hotel_2",
                                primary_text="Гранд Отель",
                                secondary_text="5 звезд, центр",
                                tertiary_text="8 000 руб/ночь",
                                image_url="https://example.com/hotel2.jpg",
                                metadata=WidgetMetadata(
                                    price=8000,
                                    rating=4.8,
                                    location="Москва, центр"
                                ),
                                actions=[
                                    Action(
                                        id="action_select_hotel_2",
                                        type="send_message",
                                        button_text="Выбрать",
                                        button_style="primary",
                                        message="Выбрать отель Гранд Отель за 8000 руб с рейтингом 4.8"
                                    )
                                ]
                            )
                        ]
                    ),
                    Widget(
                        id="widget_map_hotels",
                        type="map",
                        date=date_1,
                        config=WidgetConfig(
                            title="Карта отелей",
                            center={"lat": 55.7522, "lon": 37.6156},
                            zoom=13,
                            height=400
                        ),
                        items=[
                            Item(
                                id="marker_hotel_1",
                                primary_text="Отель Москва",
                                secondary_text="Центр, 5000 руб/ночь",
                                metadata=WidgetMetadata(
                                    coordinates={"lat": 55.7522, "lon": 37.6156},
                                    marker_color="red",
                                    marker_icon="hotel"
                                ),
                                actions=[
                                    Action(
                                        id="action_map_hotel_1",
                                        type="send_message",
                                        button_text="Подробнее",
                                        message="Показать детали отеля Отель Москва"
                                    )
                                ]
                            )
                        ]
                    )
                ]
            ),
            TimelineDate(
                date=date_2,
                label="День 2",
                widgets=[
                    Widget(
                        id="widget_guides_day2",
                        type="text_list",
                        date=date_2,
                        config=WidgetConfig(
                            title="Выберите гида",
                            layout="spacious"
                        ),
                        items=[
                            Item(
                                id="guide_1",
                                primary_text="Иван Иванов",
                                secondary_text="Экскурсии по Москве",
                                tertiary_text="Опыт 5 лет, рейтинг 4.8",
                                image_url="https://example.com/guide1.jpg",
                                icon="👨‍🏫",
                                metadata=WidgetMetadata(rating=4.8),
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
                                primary_text="Мария Петрова",
                                secondary_text="Экскурсии по Красной площади",
                                tertiary_text="Опыт 3 года, рейтинг 4.6",
                                image_url="https://example.com/guide2.jpg",
                                icon="👩‍🏫",
                                metadata=WidgetMetadata(rating=4.6),
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
                    ),
                    Widget(
                        id="widget_audio_tour",
                        type="audio",
                        date=date_2,
                        config=WidgetConfig(title="Аудио экскурсия"),
                        items=[
                            Item(
                                id="audio_1",
                                primary_text="Экскурсия по Красной площади",
                                secondary_text="Продолжительность: 1 час",
                                metadata=WidgetMetadata(
                                    audio_url="https://example.com/audio/tour1.mp3",
                                    duration=3600,
                                    thumbnail_url="https://example.com/audio/tour1.jpg"
                                ),
                                actions=[
                                    Action(
                                        id="action_download_audio",
                                        type="open_url",
                                        button_text="Скачать",
                                        url="https://example.com/audio/tour1.mp3"
                                    )
                                ]
                            )
                        ]
                    )
                ]
            ),
            TimelineDate(
                date=date_3,
                label="День 3",
                widgets=[
                    Widget(
                        id="widget_timeline_events",
                        type="timeline",
                        date=date_3,
                        config=WidgetConfig(
                            title="Расписание на день",
                            orientation="vertical"
                        ),
                        items=[
                            Item(
                                id="event_1",
                                primary_text="Прибытие в отель",
                                secondary_text="10:00",
                                metadata=WidgetMetadata(
                                    datetime=f"{date_3}T10:00:00",
                                    status="upcoming"
                                ),
                                actions=[
                                    Action(
                                        id="action_event_details_1",
                                        type="send_message",
                                        button_text="Подробнее",
                                        message="Детали события: Прибытие в отель в 10:00"
                                    )
                                ]
                            ),
                            Item(
                                id="event_2",
                                primary_text="Экскурсия по центру",
                                secondary_text="14:00",
                                metadata=WidgetMetadata(
                                    datetime=f"{date_3}T14:00:00",
                                    status="upcoming"
                                ),
                                actions=[
                                    Action(
                                        id="action_event_details_2",
                                        type="send_message",
                                        button_text="Подробнее",
                                        message="Детали события: Экскурсия по центру в 14:00"
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )

    after_timeline = [
        Widget(
            id="widget_summary",
            type="text",
            date=date_3,
            config=WidgetConfig(title="Итоговая информация"),
            items=[
                Item(
                    id="text_summary",
                    primary_text="Путешествие спланировано!",
                    secondary_text="Все детали сохранены. Приятной поездки!",
                    metadata=WidgetMetadata(format="plain")
                )
            ]
        )
    ]

    return WidgetViewResponse(
        view_id="travel_view_123",
        title="Планирование путешествия в Москву",
        metadata=ViewMetadata(
            session_id=session_id,
            context="travel",
            updated_at=datetime.now().isoformat()
        ),
        timeline=timeline,
        widgets=ViewWidgets(
            before_timeline=before_timeline,
            after_timeline=after_timeline
        )
    )


def _get_savings_view(session_id: Optional[str]) -> WidgetViewResponse:
    today = datetime.now()
    date_1 = today.strftime("%Y-%m-%d")

    before_timeline = [
        Widget(
            id="widget_progress",
            type="progress",
            date=date_1,
            config=WidgetConfig(title="Прогресс накопления"),
            items=[
                Item(
                    id="progress_1",
                    primary_text="Накоплено 1 500 000 из 3 000 000 руб",
                    secondary_text="50% завершено",
                    metadata=WidgetMetadata(
                        current=1500000,
                        total=3000000,
                        percentage=50,
                        unit="руб"
                    ),
                    actions=[
                        Action(
                            id="action_show_details",
                            type="send_message",
                            button_text="Подробнее",
                            message="Показать детали накопления на квартиру"
                        )
                    ]
                )
            ]
        ),
        Widget(
            id="widget_chart",
            type="chart",
            date=date_1,
            config=WidgetConfig(
                title="Статистика накоплений",
                chart_type="line"
            ),
            items=[
                Item(
                    id="chart_1",
                    primary_text="График накоплений",
                    metadata=WidgetMetadata(
                        data=[
                            {"label": "Янв", "value": 100000},
                            {"label": "Фев", "value": 250000},
                            {"label": "Мар", "value": 400000},
                            {"label": "Апр", "value": 550000},
                            {"label": "Май", "value": 700000},
                            {"label": "Июн", "value": 850000},
                            {"label": "Июл", "value": 1000000},
                            {"label": "Авг", "value": 1150000},
                            {"label": "Сен", "value": 1300000},
                            {"label": "Окт", "value": 1450000},
                            {"label": "Ноя", "value": 1500000}
                        ],
                        labels=["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                               "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь"],
                        colors=["#4CAF50"]
                    )
                )
            ]
        ),
        Widget(
            id="widget_stepper",
            type="stepper",
            date=date_1,
            config=WidgetConfig(
                title="Этапы накопления",
                orientation="horizontal"
            ),
            items=[
                Item(
                    id="step_1",
                    primary_text="Начало накопления",
                    metadata=WidgetMetadata(
                        step_number=1,
                        status="completed",
                        completed=True
                    )
                ),
                Item(
                    id="step_2",
                    primary_text="50% накоплено",
                    metadata=WidgetMetadata(
                        step_number=2,
                        status="active",
                        completed=False
                    )
                ),
                Item(
                    id="step_3",
                    primary_text="Выбор квартиры",
                    metadata=WidgetMetadata(
                        step_number=3,
                        status="pending",
                        completed=False
                    )
                )
            ]
        ),
        Widget(
            id="widget_button_add",
            type="button",
            date=date_1,
            config=WidgetConfig(title="Действия"),
            items=[
                Item(
                    id="btn_add_money",
                    primary_text="Добавить сумму",
                    icon="💰",
                    actions=[
                        Action(
                            id="action_add_money",
                            type="send_message",
                            button_text="Добавить",
                            button_style="primary",
                            message="Хочу добавить сумму к накоплениям"
                        )
                    ]
                ),
                Item(
                    id="btn_show_options",
                    primary_text="Показать варианты квартир",
                    icon="🏠",
                    actions=[
                        Action(
                            id="action_show_apartments",
                            type="send_message",
                            button_text="Показать",
                            button_style="secondary",
                            message="Показать варианты квартир за 3 000 000 руб"
                        )
                    ]
                )
            ]
        )
    ]

    return WidgetViewResponse(
        view_id="savings_view_123",
        title="Накопление на квартиру",
        metadata=ViewMetadata(
            session_id=session_id,
            context="savings",
            updated_at=datetime.now().isoformat()
        ),
        timeline=None,
        widgets=ViewWidgets(
            before_timeline=before_timeline,
            after_timeline=[]
        )
    )


def _get_default_view(session_id: Optional[str]) -> WidgetViewResponse:
    today = datetime.now()
    date_1 = today.strftime("%Y-%m-%d")

    before_timeline = [
        Widget(
            id="widget_welcome",
            type="text",
            date=date_1,
            config=WidgetConfig(title="Добро пожаловать"),
            items=[
                Item(
                    id="text_welcome",
                    primary_text="Привет! Я помогу спланировать путешествие.",
                    secondary_text="Выберите один из вариантов ниже.",
                    metadata=WidgetMetadata(format="plain")
                )
            ]
        ),
        Widget(
            id="widget_actions",
            type="button",
            date=date_1,
            config=WidgetConfig(title="Выберите действие"),
            items=[
                Item(
                    id="btn_travel",
                    primary_text="Планирование путешествия",
                    icon="✈️",
                    actions=[
                        Action(
                            id="action_travel",
                            type="send_message",
                            button_text="Начать планирование",
                            button_style="primary",
                            message="Хочу спланировать путешествие"
                        )
                    ]
                ),
                Item(
                    id="btn_savings",
                    primary_text="Накопление на квартиру",
                    icon="🏠",
                    actions=[
                        Action(
                            id="action_savings",
                            type="send_message",
                            button_text="Показать прогресс",
                            button_style="secondary",
                            message="Показать прогресс накопления на квартиру"
                        )
                    ]
                )
            ]
        )
    ]

    return WidgetViewResponse(
        view_id="default_view_123",
        title="Главная",
        metadata=ViewMetadata(
            session_id=session_id,
            context="default",
            updated_at=datetime.now().isoformat()
        ),
        timeline=None,
        widgets=ViewWidgets(
            before_timeline=before_timeline,
            after_timeline=[]
        )
    )


@router.post("/action", response_model=WidgetActionResponse)
async def execute_widget_action(action_request: WidgetActionRequest):
    if action_request.form_data:
        return WidgetActionResponse(
            success=True,
            message="Форма успешно отправлена",
            data={"action_id": action_request.action_id, "form_data": action_request.form_data}
        )
    else:
        return WidgetActionResponse(
            success=True,
            message=f"Действие {action_request.action_id} выполнено",
            data={"action_id": action_request.action_id}
        )

