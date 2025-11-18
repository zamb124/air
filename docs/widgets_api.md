# API контракт для виджетов

## Описание

Универсальная система виджетов для отображения различных типов контента в мобильных приложениях и на веб-сайтах. Виджеты поддерживают интерактивность, таймлайны, формы и различные типы действий.

## Основные концепции

### Виджет
Универсальный UI-компонент, независимый от домена. В виджеты можно поместить любые данные (отели, билеты, гиды и т.д.).

### Элемент (Item)
Единица данных внутри виджета. Имеет универсальную структуру с полями для текста, изображений, метаданных и действий.

### Действие (Action)
Определяет поведение при взаимодействии с виджетом или элементом (отправка сообщения в чат, открытие URL, навигация и т.д.).

### Дата виджета
Виджет может иметь поле `date`, которое указывает фронтенду, когда его показывать в сетке/таблице.

## API Endpoints

### GET /widgets/view

Получение представления (view) с виджетами для пользователя/сессии.

**Query параметры:**
- `session_id` (string, опционально) - идентификатор сессии пользователя
- `context` (string, опционально) - контекст использования (travel, savings и т.д.)

**Response:**
```json
{
  "view_id": "view_123",
  "title": "Планирование путешествия",
  "metadata": {
    "session_id": "session_123",
    "context": "travel",
    "updated_at": "2025-01-15T10:00:00Z"
  },
  "timeline": {
    "enabled": true,
    "start_date": "2025-01-15",
    "end_date": "2025-01-20",
    "dates": [
      {
        "date": "2025-01-15",
        "label": "День 1",
        "widgets": [...]
      }
    ]
  },
  "widgets": {
    "before_timeline": [...],
    "after_timeline": [...]
  }
}
```

### POST /widgets/action

Выполнение действия от виджета.

**Body:**
```json
{
  "view_id": "view_123",
  "widget_id": "widget_1",
  "item_id": "item_1",
  "action_id": "action_1",
  "session_id": "session_123",
  "form_data": {...},
  "context": {...}
}
```

## Структура виджета

### Базовая структура

```json
{
  "id": "widget_123",
  "type": "button" | "card_carousel" | "text_list" | "map" | "image" | "audio" | 
          "video" | "form" | "calendar" | "timeline" | "progress" | "chart" | 
          "accordion" | "tabs" | "stepper" | "divider" | "text",
  "date": "2025-01-15",  // опционально, дата для отображения на фронтенде
  "config": {
    "title": "string",
    "subtitle": "string",
    "style": {...}
  },
  "items": [...],
  "fields": [...],  // для form
  "actions": [...]
}
```

### Структура элемента (Item)

```json
{
  "id": "item_1",
  "primary_text": "string",
  "secondary_text": "string",
  "tertiary_text": "string",
  "image_url": "string",
  "icon": "string",
  "badge": "string",
  "metadata": {
    "price": 5000,
    "rating": 4.5,
    "coordinates": {"lat": 55.7522, "lon": 37.6156}
  },
  "actions": [...]
}
```

### Структура действия (Action)

```json
{
  "id": "action_1",
  "type": "send_message" | "open_url" | "navigate" | "update_view" | 
          "submit_form" | "validate_form" | "show_widget",
  "button_text": "string",
  "button_style": "primary" | "secondary" | "outline" | "danger" | "link",
  "message": "string",
  "message_template": "string",
  "url": "string",
  "target": "string",
  "validation": {...},
  "required_fields": ["field1"],
  "condition": {...}
}
```

## Типы виджетов

### button

Простая кнопка с действием.

```json
{
  "type": "button",
  "config": {
    "title": "Выберите действие"
  },
  "items": [
    {
      "id": "btn_1",
      "primary_text": "Найти билеты",
      "icon": "✈️",
      "actions": [{
        "type": "send_message",
        "message": "Показать варианты авиабилетов",
        "button_text": "Найти билеты",
        "button_style": "primary"
      }]
    }
  ]
}
```

### card_carousel

Горизонтальная карусель карточек.

```json
{
  "type": "card_carousel",
  "config": {
    "title": "Варианты отелей",
    "show_dots": true,
    "auto_play": false
  },
  "items": [...]
}
```

### text_list

Вертикальный список элементов.

```json
{
  "type": "text_list",
  "config": {
    "title": "Список гидов",
    "layout": "compact" | "spacious"
  },
  "items": [...]
}
```

### form

Форма с полями ввода.

**Структура поля:**
```json
{
  "id": "field_name",
  "type": "text" | "email" | "tel" | "number" | "date" | "time" | 
          "datetime" | "select" | "multiselect" | "checkbox" | "radio" | 
          "textarea" | "file" | "password",
  "label": "Имя",
  "placeholder": "Введите имя",
  "required": true,
  "validation": {
    "min_length": 2,
    "max_length": 50,
    "pattern": "...",
    "error_message": "..."
  },
  "options": [...],
  "default_value": "...",
  "help_text": "..."
}
```

**Пример формы:**
```json
{
  "type": "form",
  "config": {
    "title": "Забронировать отель"
  },
  "fields": [
    {
      "id": "name",
      "type": "text",
      "label": "Ваше имя",
      "required": true,
      "validation": {"min_length": 2}
    },
    {
      "id": "email",
      "type": "email",
      "label": "Email",
      "required": true
    }
  ],
  "actions": [{
    "type": "submit_form",
    "message_template": "Забронировать отель для {name}, email: {email}",
    "button_text": "Забронировать"
  }]
}
```

### map

Карта с маркерами.

```json
{
  "type": "map",
  "config": {
    "title": "Карта отелей",
    "center": {"lat": 55.7522, "lon": 37.6156},
    "zoom": 13,
    "height": 400
  },
  "items": [
    {
      "id": "marker_1",
      "primary_text": "Отель Москва",
      "metadata": {
        "lat": 55.7522,
        "lon": 37.6156,
        "marker_color": "red"
      },
      "actions": [...]
    }
  ]
}
```

### image

Изображение.

```json
{
  "type": "image",
  "config": {
    "aspect_ratio": "16:9",
    "fit": "cover" | "contain"
  },
  "items": [
    {
      "id": "img_1",
      "image_url": "https://...",
      "primary_text": "Красная площадь",
      "actions": [...]
    }
  ]
}
```

### audio

Аудио проигрыватель.

```json
{
  "type": "audio",
  "config": {
    "title": "Аудио экскурсия"
  },
  "items": [
    {
      "id": "audio_1",
      "primary_text": "Экскурсия по Красной площади",
      "metadata": {
        "audio_url": "https://...",
        "duration": 3600,
        "thumbnail_url": "..."
      }
    }
  ]
}
```

### video

Видео проигрыватель.

```json
{
  "type": "video",
  "config": {
    "title": "Видео обзор",
    "autoplay": false,
    "controls": true
  },
  "items": [
    {
      "id": "video_1",
      "metadata": {
        "video_url": "https://...",
        "thumbnail_url": "...",
        "duration": 300
      }
    }
  ]
}
```

### calendar

Календарь для выбора даты.

```json
{
  "type": "calendar",
  "config": {
    "title": "Выберите дату",
    "mode": "single" | "range",
    "min_date": "2025-01-01",
    "max_date": "2025-12-31"
  },
  "items": [
    {
      "id": "date_2025-01-15",
      "metadata": {
        "date": "2025-01-15",
        "available": true,
        "price": 5000
      },
      "actions": [...]
    }
  ]
}
```

### timeline

Таймлайн событий.

```json
{
  "type": "timeline",
  "config": {
    "title": "Путешествие",
    "orientation": "vertical" | "horizontal"
  },
  "items": [
    {
      "id": "event_1",
      "primary_text": "Прибытие в отель",
      "secondary_text": "15 янв, 14:00",
      "metadata": {
        "datetime": "2025-01-15T14:00:00",
        "status": "completed" | "upcoming" | "in_progress"
      }
    }
  ]
}
```

### progress

Индикатор прогресса.

```json
{
  "type": "progress",
  "config": {
    "title": "Прогресс накопления"
  },
  "items": [
    {
      "id": "progress_1",
      "primary_text": "Накоплено 150 000 из 300 000 руб",
      "metadata": {
        "current": 150000,
        "total": 300000,
        "percentage": 50,
        "unit": "руб"
      }
    }
  ]
}
```

### chart

График или диаграмма.

```json
{
  "type": "chart",
  "config": {
    "title": "Статистика расходов",
    "chart_type": "line" | "bar" | "pie" | "area"
  },
  "items": [
    {
      "id": "chart_1",
      "metadata": {
        "data": [
          {"label": "Янв", "value": 5000},
          {"label": "Фев", "value": 7000}
        ],
        "labels": ["Январь", "Февраль"]
      }
    }
  ]
}
```

### accordion

Аккордеон (раскрывающиеся секции).

```json
{
  "type": "accordion",
  "config": {
    "title": "Часто задаваемые вопросы",
    "multiple": true
  },
  "items": [
    {
      "id": "faq_1",
      "primary_text": "Как отменить бронирование?",
      "secondary_text": "Вы можете отменить бронирование..."
    }
  ]
}
```

### tabs

Вкладки.

```json
{
  "type": "tabs",
  "config": {
    "title": "Информация"
  },
  "items": [
    {
      "id": "tab_1",
      "primary_text": "Отели",
      "metadata": {
        "tab_id": "hotels"
      }
    }
  ]
}
```

### stepper

Степпер (шаги процесса).

```json
{
  "type": "stepper",
  "config": {
    "title": "Шаги планирования",
    "orientation": "horizontal" | "vertical"
  },
  "items": [
    {
      "id": "step_1",
      "primary_text": "Выбор отеля",
      "metadata": {
        "step_number": 1,
        "status": "completed" | "active" | "pending",
        "completed": true
      }
    }
  ]
}
```

### divider

Разделитель.

```json
{
  "type": "divider",
  "config": {
    "label": "Или"
  }
}
```

### text

Текстовый блок.

```json
{
  "type": "text",
  "config": {
    "title": "Информация"
  },
  "items": [
    {
      "id": "text_1",
      "primary_text": "Привет! Я помогу спланировать путешествие.",
      "metadata": {
        "format": "markdown" | "html" | "plain"
      }
    }
  ]
}
```

## Использование даты виджета

Поле `date` в виджете используется фронтендом для:
- Группировки виджетов по датам в сетке/календаре
- Фильтрации виджетов по дате
- Сортировки виджетов хронологически
- Отображения виджетов в соответствующие дни таймлайна

Пример:
```json
{
  "id": "widget_hotel_selection",
  "type": "card_carousel",
  "date": "2025-01-15",
  "config": {
    "title": "Выберите отель на 15 января"
  },
  "items": [...]
}
```

## Примеры использования

### Планирование путешествия

```json
{
  "view_id": "travel_plan_123",
  "title": "Планирование путешествия в Москву",
  "widgets": {
    "before_timeline": [
      {
        "id": "widget_flights",
        "type": "card_carousel",
        "date": "2025-01-14",
        "config": {"title": "Выберите билеты"},
        "items": [
          {
            "id": "flight_1",
            "primary_text": "SU 123 Москва → Сочи",
            "secondary_text": "15 янв, 10:00, от 5000 руб",
            "actions": [{
              "type": "send_message",
              "message": "Выбрать рейс SU 123",
              "button_text": "Выбрать"
            }]
          }
        ]
      }
    ],
    "after_timeline": []
  },
  "timeline": {
    "enabled": true,
    "dates": [
      {
        "date": "2025-01-15",
        "widgets": [
          {
            "id": "widget_hotel_day1",
            "type": "card_carousel",
            "date": "2025-01-15",
            "config": {"title": "Отели на 15 января"},
            "items": [...]
          }
        ]
      }
    ]
  }
}
```

### Накопление на квартиру

```json
{
  "view_id": "savings_123",
  "title": "Накопление на квартиру",
  "widgets": {
    "before_timeline": [
      {
        "id": "widget_progress",
        "type": "progress",
        "date": "2025-01-15",
        "config": {"title": "Прогресс"},
        "items": [
          {
            "id": "progress_1",
            "primary_text": "Накоплено 1 500 000 из 3 000 000 руб",
            "metadata": {
              "current": 1500000,
              "total": 3000000,
              "percentage": 50
            }
          }
        ]
      }
    ]
  }
}
```

