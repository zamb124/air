# Документация API виджетов для фронтенда

## Описание

Универсальная система виджетов для отображения различных типов контента. Виджеты поддерживают интерактивность, группировку по датам, таймлайны и различные типы действий.

## API Endpoints

### GET /widgets/view

Получение представления (view) с виджетами.

**Query параметры:**
- `goal_id` (string, опционально) - идентификатор цели
- `context` (string, опционально) - контекст использования (`travel`, `savings`, или `default`)

**Response:**
```json
{
  "view_id": "travel_view_123",
  "title": "Поездка в Питер",
  "goal_id": "goal_123",
  "context": "travel",
  "widgets": [...]
}
```

### POST /widgets/action

Выполнение действия от виджета.

**Body:**
```json
{
  "view_id": "travel_view_123",
  "widget_id": "widget_flights",
  "item_id": "flight_1",
  "action_id": "action_select_flight_1",
  "goal_id": "goal_123",
  "data": {}
}
```

**Response:**
```json
{
  "success": true,
  "message": "Действие action_select_flight_1 выполнено",
  "data": {
    "action_id": "action_select_flight_1",
    "data": {}
  }
}
```

## Структура данных

### WidgetViewResponse

Корневой объект ответа с виджетами.

```typescript
{
  view_id: string;           // Уникальный идентификатор представления
  title: string;             // Заголовок представления
  goal_id?: string;          // Идентификатор цели (опционально)
  context?: string;          // Контекст (travel, savings, default)
  widgets: Widget[];         // Список виджетов
}
```

### Widget

Базовый виджет.

```typescript
{
  id: string;                // Уникальный идентификатор виджета
  type: "large_card_carousel" | "small_card_carousel" | "card_with_button" | "quiz" | "map";
  title?: string;            // Заголовок виджета
  group?: string;            // Группа для группировки виджетов (например, дата)
  group_order?: number;      // Порядок в группе
  datetime?: string;         // Дата и время в формате ISO 8601 (например, "2025-01-15T10:00:00")
  order?: number;            // Порядок виджета
  items?: Item[];            // Список элементов (для carousel и card_with_button)
  questions?: QuizQuestion[]; // Список вопросов (для quiz)
  data?: Record<string, any>; // Произвольные данные (для map)
  actions?: Action[];        // Действия на уровне виджета
}
```

### Item

Элемент внутри виджета (карточка в карусели, элемент карты и т.д.).

```typescript
{
  id: string;                // Уникальный идентификатор элемента
  text: string;              // Основной текст
  subtitle?: string;         // Подзаголовок
  image_url?: string;        // URL изображения
  icon?: string;             // Эмодзи или иконка (например, "✈️")
  metadata?: Record<string, any>; // Метаданные (цена, рейтинг, адрес и т.д.)
  actions?: Action[];        // Действия на уровне элемента
}
```

### Action

Действие при взаимодействии с виджетом или элементом.

```typescript
{
  id: string;                // Уникальный идентификатор действия
  type: "send_message" | "open_url";
  button_text: string;       // Текст кнопки
  message?: string;          // Сообщение для отправки (если type="send_message")
  url?: string;              // URL для открытия (если type="open_url")
}
```

### QuizQuestion

Вопрос для квиза.

```typescript
{
  id: string;                // Уникальный идентификатор вопроса
  text: string;              // Текст вопроса
  options: QuizOption[];     // Варианты ответов
}
```

### QuizOption

Вариант ответа в квизе.

```typescript
{
  id: string;                // Уникальный идентификатор варианта
  text: string;              // Текст варианта
  is_correct?: boolean;      // Является ли правильным ответом (опционально)
}
```

## Типы виджетов

В системе доступны следующие типы виджетов:

1. **`large_card_carousel`** - Большая горизонтальная карусель карточек
2. **`small_card_carousel`** - Небольшая горизонтальная карусель карточек
3. **`card_with_button`** - Карточка с одной или несколькими кнопками
4. **`quiz`** - Квиз с вопросами и вариантами ответов
5. **`map`** - Интерактивная карта с маркерами

### 1. large_card_carousel

Большая горизонтальная карусель карточек. Используется для отображения списка вариантов (рейсы, отели, машины и т.д.).

**Структура:**
- Обязательно: `items` - список элементов
- Опционально: `title`, `group`, `datetime`, `order`

**Пример:**
```json
{
  "id": "widget_flights",
  "type": "large_card_carousel",
  "title": "Выберите авиабилеты",
  "group": "Подготовка",
  "group_order": 1,
  "datetime": "2025-01-15T10:00:00",
  "order": 1,
  "items": [
    {
      "id": "flight_1",
      "text": "SU 123 Москва → Сочи",
      "subtitle": "15 янв, 10:00, от 5 000 руб",
      "icon": "✈️",
      "metadata": {
        "price": 5000
      },
      "actions": [
        {
          "id": "action_select_flight_1",
          "type": "send_message",
          "button_text": "Выбрать",
          "message": "Выбрать рейс SU 123 Москва-Сочи на 15 янв 10:00 за 5000 руб"
        }
      ]
    }
  ]
}
```

**Особенности отображения:**
- Горизонтальная прокрутка
- Крупные карточки с изображениями/иконками
- Подходит для важного контента, требующего внимания

### 2. small_card_carousel

Небольшая горизонтальная карусель карточек. Используется для дополнительных вариантов (рестораны, гиды, этапы и т.д.).

**Структура:**
- Обязательно: `items` - список элементов
- Опционально: `title`, `group`, `datetime`, `order`

**Пример:**
```json
{
  "id": "widget_restaurants_day1",
  "type": "small_card_carousel",
  "title": "Завтрак в ресторане",
  "group": "2025-01-15",
  "group_order": 2,
  "datetime": "2025-01-15T11:00:00",
  "order": 2,
  "items": [
    {
      "id": "restaurant_1",
      "text": "Mad Espresso",
      "image_url": "https://example.com/rest1.jpg",
      "actions": [
        {
          "id": "action_restaurant_1",
          "type": "send_message",
          "button_text": "Выбрать",
          "message": "Показать детали ресторана Mad Espresso"
        }
      ]
    }
  ]
}
```

**Особенности отображения:**
- Горизонтальная прокрутка
- Компактные карточки
- Подходит для дополнительного контента

### 3. card_with_button

Карточка с одной или несколькими кнопками. Используется для отображения одного объекта с действиями (отель, прогресс и т.д.).

**Структура:**
- Обязательно: `items` - список элементов (обычно один элемент)
- Обязательно: `actions` - действия на уровне виджета
- Опционально: `title`, `group`, `datetime`, `order`

**Пример:**
```json
{
  "id": "widget_hotel_day1",
  "type": "card_with_button",
  "title": "Ваш отель",
  "group": "2025-01-15",
  "group_order": 2,
  "datetime": "2025-01-15T11:00:00",
  "order": 1,
  "items": [
    {
      "id": "hotel_1",
      "text": "Corinthia",
      "subtitle": "Заселение в 11:00, 7 декабря. Выселение до 9:00, 9 декабря",
      "image_url": "https://example.com/hotel1.jpg",
      "metadata": {
        "address": "г. Санкт-Петербург, Невский пр-т, д. 57"
      }
    }
  ],
  "actions": [
    {
      "id": "action_open_map",
      "type": "open_url",
      "button_text": "Открыть на карте",
      "url": "https://maps.yandex.ru/..."
    }
  ]
}
```

**Особенности отображения:**
- Вертикальная карточка
- Кнопки отображаются внизу карточки или внутри
- Подходит для отображения одного объекта

### 4. quiz

Квиз с вопросами и вариантами ответов.

**Структура:**
- Обязательно: `questions` - список вопросов
- Опционально: `title`, `group`, `datetime`, `order`

**Пример:**
```json
{
  "id": "widget_quiz",
  "type": "quiz",
  "title": "Первый квиз",
  "group": "Первый квиз",
  "group_order": 2,
  "datetime": "2025-01-15T10:00:00",
  "order": 1,
  "questions": [
    {
      "id": "question_1",
      "text": "Какой тип ИИ представлен голосовым помощником?",
      "options": [
        {
          "id": "opt_1",
          "text": "Реактивный ИИ (Reactive AI)",
          "is_correct": false
        },
        {
          "id": "opt_2",
          "text": "Общий ИИ (General AI)",
          "is_correct": false
        },
        {
          "id": "opt_3",
          "text": "Узкий ИИ (Narrow AI)",
          "is_correct": true
        },
        {
          "id": "opt_4",
          "text": "Искусственный Суперинтеллект",
          "is_correct": false
        }
      ]
    }
  ]
}
```

**Особенности отображения:**
- Вопросы отображаются последовательно
- Варианты ответов - кликабельные кнопки или радиокнопки
- После выбора ответа можно показать правильность (если `is_correct` указан)

### 5. map

Интерактивная карта с маркерами.

**Структура:**
- Обязательно: `data` - данные карты
- Опционально: `title`, `group`, `datetime`, `order`

**Формат `data`:**
```typescript
{
  center: {
    lat: number;  // Широта центра карты
    lon: number;  // Долгота центра карты
  };
  zoom: number;   // Уровень масштабирования (1-20)
  markers: Array<{
    lat: number;  // Широта маркера
    lon: number;  // Долгота маркера
    title?: string; // Заголовок маркера (опционально)
  }>;
}
```

**Пример:**
```json
{
  "id": "widget_map_hotel",
  "type": "map",
  "title": "Карта отелей",
  "group": "2025-01-15",
  "group_order": 2,
  "datetime": "2025-01-15T11:00:00",
  "order": 3,
  "data": {
    "center": {
      "lat": 55.7522,
      "lon": 37.6156
    },
    "zoom": 13,
    "markers": [
      {
        "lat": 55.7522,
        "lon": 37.6156,
        "title": "Corinthia"
      }
    ]
  }
}
```

**Особенности отображения:**
- Интерактивная карта (можно использовать Яндекс.Карты, Google Maps и т.д.)
- Маркеры отображаются на карте
- При клике на маркер можно показать всплывающее окно с информацией

## Группировка и сортировка

Виджеты могут быть сгруппированы по датам или категориям с помощью полей `group`, `group_order`, `datetime` и `order`:

- `group` - название группы (часто это дата в формате "YYYY-MM-DD")
- `group_order` - порядок группы (меньше = выше)
- `datetime` - дата и время для таймлайна
- `order` - порядок внутри группы (меньше = выше)

**Рекомендации по отображению:**

1. Группируйте виджеты по `group`
2. Сортируйте группы по `group_order` (по возрастанию)
3. Сортируйте виджеты внутри группы по `order` (по возрастанию)
4. Используйте `datetime` для отображения в таймлайне

## Действия

В системе доступны следующие типы действий:

1. **`send_message`** - Отправка сообщения в чат
2. **`open_url`** - Открытие URL в браузере или встроенном веб-вью

### send_message

Отправляет сообщение в чат. Используется для взаимодействия с ботом/агентом.

```typescript
{
  type: "send_message";
  message: string;  // Текст сообщения, которое будет отправлено
}
```

**Обработка:**
1. При клике на кнопку отправьте `POST /widgets/action` с данными действия
2. Отправьте сообщение `message` в чат (через ваш чат-клиент)

### open_url

Открывает URL в браузере или встроенном веб-вью.

```typescript
{
  type: "open_url";
  url: string;  // URL для открытия
}
```

**Обработка:**
1. При клике на кнопку отправьте `POST /widgets/action` с данными действия
2. Откройте `url` в браузере или встроенном веб-вью

## Полные примеры ответов

### Пример 1: Travel context

```json
{
  "view_id": "travel_view_123",
  "title": "Поездка в Питер",
  "goal_id": "goal_123",
  "context": "travel",
  "widgets": [
    {
      "id": "widget_flights",
      "type": "large_card_carousel",
      "title": "Выберите авиабилеты",
      "group": "Подготовка",
      "group_order": 1,
      "datetime": "2025-01-15T10:00:00",
      "order": 1,
      "items": [
        {
          "id": "flight_1",
          "text": "SU 123 Москва → Сочи",
          "subtitle": "15 янв, 10:00, от 5 000 руб",
          "icon": "✈️",
          "metadata": {"price": 5000},
          "actions": [
            {
              "id": "action_select_flight_1",
              "type": "send_message",
              "button_text": "Выбрать",
              "message": "Выбрать рейс SU 123 Москва-Сочи на 15 янв 10:00 за 5000 руб"
            }
          ]
        }
      ]
    },
    {
      "id": "widget_hotel_day1",
      "type": "card_with_button",
      "title": "Ваш отель",
      "group": "2025-01-15",
      "group_order": 2,
      "datetime": "2025-01-15T11:00:00",
      "order": 1,
      "items": [
        {
          "id": "hotel_1",
          "text": "Corinthia",
          "subtitle": "Заселение в 11:00, 7 декабря. Выселение до 9:00, 9 декабря",
          "image_url": "https://example.com/hotel1.jpg",
          "metadata": {"address": "г. Санкт-Петербург, Невский пр-т, д. 57"}
        }
      ],
      "actions": [
        {
          "id": "action_open_map",
          "type": "open_url",
          "button_text": "Открыть на карте",
          "url": "https://maps.yandex.ru/..."
        }
      ]
    }
  ]
}
```

### Пример 2: Savings context

```json
{
  "view_id": "savings_view_123",
  "title": "Покупка китайской машины",
  "goal_id": "goal_456",
  "context": "savings",
  "widgets": [
    {
      "id": "widget_car_selection",
      "type": "large_card_carousel",
      "title": "Машины на выбор",
      "group": "Выбор машины",
      "group_order": 1,
      "datetime": "2025-01-15T10:00:00",
      "order": 1,
      "items": [
        {
          "id": "car_1",
          "text": "Geely Xingyuan",
          "subtitle": "субкомпактный электромобиль-хетчбэк, разработанный китайской компанией Geely Auto",
          "image_url": "https://example.com/car1.jpg",
          "metadata": {"price": 6500000},
          "actions": [
            {
              "id": "action_calculate_cost",
              "type": "send_message",
              "button_text": "Рассчитать стоимость",
              "message": "Рассчитать стоимость машины Geely Xingyuan"
            }
          ]
        }
      ]
    },
    {
      "id": "widget_progress",
      "type": "card_with_button",
      "title": "Прогресс накопления",
      "group": "План накопления",
      "group_order": 2,
      "datetime": "2025-01-15T11:00:00",
      "order": 2,
      "items": [
        {
          "id": "progress_1",
          "text": "Накоплено 1 500 000 из 3 000 000 руб",
          "subtitle": "50% завершено",
          "metadata": {
            "current": 1500000,
            "total": 3000000,
            "percentage": 50
          }
        }
      ],
      "actions": [
        {
          "id": "action_show_details",
          "type": "send_message",
          "button_text": "Подробнее",
          "message": "Показать детали накопления"
        }
      ]
    }
  ]
}
```

## Рекомендации по реализации

1. **Обработка отсутствующих полей**: Все поля кроме обязательных (`id`, `type`) являются опциональными. Всегда проверяйте наличие полей перед использованием.

2. **Загрузка изображений**: Используйте `image_url` для загрузки изображений. Рекомендуется показывать placeholder во время загрузки.

3. **Обработка действий**: При клике на кнопку действия:
   - Сначала отправьте `POST /widgets/action` с данными действия
   - Затем выполните само действие (отправка сообщения или открытие URL)

4. **Группировка**: Группируйте виджеты визуально по полю `group` (например, разделители, заголовки групп).

5. **Таймлайн**: Используйте поле `datetime` для отображения виджетов в хронологическом порядке на таймлайне.

6. **Метаданные**: Поле `metadata` может содержать любые дополнительные данные (цена, рейтинг, координаты и т.д.). Используйте их для дополнительного форматирования отображения.

7. **Иконки**: Поле `icon` содержит эмодзи или текстовое обозначение. Отображайте его рядом с текстом элемента.
