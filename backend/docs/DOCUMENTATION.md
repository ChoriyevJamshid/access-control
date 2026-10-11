# Система контроля доступа — Access Control System

**Версия:** 1.0.2  
**Дата документа:** 2026-04-03  
**Автор:** ChoriyevJamshid  
**Язык реализации:** Python 3 / Django 5.2

---

## Содержание

1. [Обзор проекта](#1-обзор-проекта)
2. [Технологический стек](#2-технологический-стек)
3. [Архитектура системы](#3-архитектура-системы)
4. [Модели данных](#4-модели-данных)
5. [Бизнес-логика и алгоритмы](#5-бизнес-логика-и-алгоритмы)
6. [API документация](#6-api-документация)
7. [Асинхронные задачи Celery](#7-асинхронные-задачи-celery)
8. [Развёртывание и настройка](#8-развёртывание-и-настройка)
9. [Управляющие команды](#9-управляющие-команды)
10. [Рабочие процессы системы](#10-рабочие-процессы-системы)

---

## 1. Обзор проекта

**Access Control System** — это многофункциональная серверная система для управления контролем доступа сотрудников на предприятии. Система предоставляет инструменты для:

- **Учёта рабочего времени** — фиксация событий входа/выхода сотрудников, автоматическое формирование рабочих сессий и ежедневной посещаемости.
- **Управления персоналом** — создание и ведение базы сотрудников с историей изменения компенсаций и графиков работы.
- **Расчёта заработной платы** — автоматический расчёт зарплаты на основе фактически отработанного времени, учёт опозданий, переработок и досрочных уходов.
- **Аналитического дашборда** — сводная информация о посещаемости, статистика за 7 дней, автоматические предупреждения.
- **Управления предприятием** — иерархическая структура отделов, управление несколькими уровнями организации.

Система построена на принципах чистой архитектуры с разделением ответственности: **Models → Selectors → Services → Serializers → Views**.

---

## 2. Технологический стек

### Основной фреймворк

| Технология | Версия | Назначение |
|---|---|---|
| Python | 3.12+ | Язык программирования |
| Django | 5.2 | Веб-фреймворк |
| Django REST Framework | 3.16.1 | REST API |
| djangorestframework-simplejwt | 5.5.1 | JWT аутентификация |

### База данных

| Технология | Версия | Назначение |
|---|---|---|
| PostgreSQL | 14+ | Основная СУБД (production) |
| SQLite | встроенная | СУБД для разработки |
| PgBouncer | — | Пул соединений к PostgreSQL |

### Очередь задач

| Технология | Версия | Назначение |
|---|---|---|
| Celery | 5.6.2 | Асинхронная очередь задач |
| django-celery-beat | 2.8.1 | Периодические задачи |
| Redis | 7.2.0 | Брокер сообщений и backend результатов |

### Реальное время и безопасность

| Технология | Версия | Назначение |
|---|---|---|
| Django Channels | 4.3.2 | WebSocket / async поддержка |
| django-cors-headers | 4.9.0 | CORS политика |
| argon2-cffi | 25.1.0 | Хэширование паролей (Argon2) |
| django-allauth | 65.14.3 | Социальная аутентификация |

### Инфраструктура и документация

| Технология | Версия | Назначение |
|---|---|---|
| drf-spectacular | 0.29.0 | OpenAPI/Swagger документация |
| gunicorn | 25.1.0 | WSGI сервер |
| uvicorn | 0.41.0 | ASGI сервер |
| whitenoise | 6.11.1 | Раздача статических файлов |
| django-unfold | 0.66.0 | Современный интерфейс Django Admin |
| django-filter | 25.2 | Фильтрация в API |
| django-debug-toolbar | 6.2.0 | Отладочная панель (dev) |
| openpyxl | 3.1.5 | Генерация Excel-файлов (.xlsx) |

---

## 3. Архитектура системы

### 3.1 Структура директорий

```
access-control-system/
├── apps/                          # Django приложения
│   ├── base_models.py             # Абстрактная BaseModel (created/updated)
│   ├── users/                     # Пользователи, предприятия, отделы
│   ├── employees/                 # Сотрудники, компенсации, графики
│   ├── access_control/            # События доступа, рабочие сессии, посещаемость
│   └── payroll/                   # Расчёт зарплаты, периоды выплат
├── api/                           # REST API
│   ├── urls.py                    # Корневые URL (JWT токены)
│   └── v1/                        # API версия 1
│       ├── access_control/        # Эндпоинты контроля доступа
│       ├── employees/             # Эндпоинты управления сотрудниками
│       ├── enterprise/            # Эндпоинты предприятия и отделов
│       ├── dashboard/             # Эндпоинт дашборда
│       └── payroll/               # Эндпоинты расчёта зарплаты
├── src/                           # Настройки Django проекта
│   ├── settings/
│   │   ├── base.py                # Основная конфигурация
│   │   └── local.py               # Локальная конфигурация разработки
│   ├── urls.py                    # Корневая маршрутизация
│   └── celery_app.py              # Конфигурация Celery
├── requirements/
│   └── base.txt                   # Зависимости проекта
└── skd/
    └── tester.py                  # Скрипты тестирования API
```

### 3.2 Паттерны проектирования

Проект использует несколько ключевых паттернов:

**1. Service Layer (Сервисный слой)**  
Вся бизнес-логика инкапсулирована в файлах `services.py`. Контроллеры (views) не содержат бизнес-логики — только вызовы сервисов.

**2. Selector Pattern (Паттерн селекторов)**  
Сложные запросы к базе данных вынесены в файлы `selectors.py`. Это обеспечивает переиспользование запросов и изоляцию доступа к данным от бизнес-логики.

**3. Signal-driven Architecture (Событийная архитектура)**  
При сохранении `AccessEvent` Django сигнал (`post_save`) автоматически запускает Celery-задачу обработки рабочей сессии. Это обеспечивает асинхронность и слабую связность компонентов.

**4. Abstract Base Model**  
Все модели наследуются от `BaseModel`, который автоматически добавляет поля `created` и `updated`.

---

## 4. Модели данных

### 4.1 Предприятие и отделы (apps/users/models.py)

#### Enterprise (Предприятие)
```
- name       CharField(63)     — Название предприятия
- code       CharField(unique) — Уникальный код "ENT-XXXXXXXXXX" (авто)
- owner      OneToOneField → User — Владелец
```

#### Department (Отдел)
```
- name       CharField(63)     — Название отдела
- code       CharField(unique) — Уникальный код "DEP-XXXXXXXXXX" (авто)
- enterprise ForeignKey → Enterprise — Принадлежность к предприятию
- parent     ForeignKey → self  — Родительский отдел (иерархия)
```
Поддерживает неограниченную иерархию отделов. При сохранении предприятие автоматически берётся из родительского отдела.

### 4.2 Сотрудники (apps/employees/models.py)

#### Employee (Сотрудник)
```
- enterprise   ForeignKey → Enterprise — Предприятие
- department   ForeignKey → Department — Отдел
- first_name   CharField(31)  — Имя
- last_name    CharField(31)  — Фамилия
- middle_name  CharField(31)  — Отчество
- code         CharField(63)  — Табельный номер (уникален в рамках предприятия)
```

#### EmployeeDetail (Компенсация сотрудника)
```
- employee       ForeignKey → Employee  — Сотрудник
- salary_type    CharField choices      — Тип: HOURLY (почасовой), MONTHLY (ежемесячный)
- amount         DecimalField(14,2)     — Сумма компенсации
- effective_from DateField             — Дата начала действия
- effective_to   DateField (nullable)   — Дата окончания действия
- is_active      BooleanField           — Активна ли запись
```
Поддерживает историю изменений компенсации. В любой момент времени активна только одна запись (`is_active=True`).

#### EmployeeWorkDay (График работы)
```
- detail     ForeignKey → EmployeeDetail — Запись компенсации
- weekday    PositiveSmallInt (0-6)      — День недели (0=Пн, 6=Вс)
- from_time  TimeField                  — Начало рабочего дня
- to_time    TimeField                  — Конец рабочего дня
- hours      DurationField              — Плановое количество часов
```

### 4.3 Контроль доступа (apps/access_control/models.py)

#### AccessEvent (Событие доступа)
```
- employee   ForeignKey → Employee — Сотрудник
- timestamp  DateTimeField         — Время события (индексировано)
- type       CharField choices     — Тип: ENTER (вход) или LEAVE (выход)
```
При создании сигнал `post_save` запускает Celery-задачу `processing_work_session`.

#### WorkSession (Рабочая сессия)
```
- employee         ForeignKey → Employee — Сотрудник
- started          DateTimeField         — Начало сессии
- ended            DateTimeField (null)  — Конец сессии
- duration_seconds PositiveIntegerField  — Длительность в секундах
- closed           BooleanField          — Закрыта ли сессия
```

#### DailyAttendance (Ежедневная посещаемость)
```
- employee            ForeignKey → Employee — Сотрудник
- date                DateField             — Дата (индексировано)
- work_seconds        PositiveIntegerField  — Фактически отработанные секунды
- late_seconds        PositiveIntegerField  — Секунды опоздания
- planned_seconds     PositiveIntegerField  — Плановые секунды
- overtime_seconds    PositiveIntegerField  — Переработка в секундах
- early_leave_seconds PositiveIntegerField  — Ранний уход в секундах
```

### 4.4 Расчёт зарплаты (apps/payroll/models.py)

#### PayrollPeriod (Период выплаты)
```
- start_date DateField — Начало периода
- end_date   DateField — Конец периода
- is_closed  Boolean   — Закрыт ли период
```

#### EmployeePayroll (Зарплата сотрудника за период)
```
- employee          ForeignKey → Employee       — Сотрудник
- period            ForeignKey → PayrollPeriod  — Период
- total_work_seconds PositiveIntegerField        — Итого отработанных секунд
- total_amount      DecimalField(14,2)           — Итоговая сумма
- calculated_at     DateTimeField               — Дата расчёта
- is_finalized      Boolean                     — Подтверждён ли расчёт
```

#### PayrollItem (Позиция зарплатного расчёта)
```
- payroll     ForeignKey → EmployeePayroll — Зарплата
- type        CharField choices            — BASE, OVERTIME, BONUS, PENALTY, MANUAL
- amount      DecimalField(14,2)           — Сумма позиции
- description CharField(255)              — Описание
```

---

## 5. Бизнес-логика и алгоритмы

### 5.1 Алгоритм обработки события доступа

При поступлении события доступа (`AccessEvent`) выполняется следующая цепочка:

**Шаг 1 — Проверка дубликатов**  
`check_access_exists_service(employee, timestamp, type)` — проверяет, не было ли уже зарегистрировано аналогичное событие.

**Шаг 2 — Запуск асинхронной задачи**  
Django-сигнал `post_save` автоматически вызывает `processing_work_session.delay(access_event_id)`.

**Шаг 3 — Обработка ENTER (Вход)**
1. Проверяет, запланирован ли рабочий день для данного дня недели.
2. Закрывает предыдущую открытую сессию (если есть) с фиксацией `ended` и `duration_seconds`.
3. Создаёт новую `WorkSession` с `started = timestamp`, `closed = False`.
4. Обновляет `DailyAttendance` для закрытой сессии.

**Шаг 4 — Обработка LEAVE (Выход)**
1. Находит открытую `WorkSession`.
2. Устанавливает `ended = timestamp`, вычисляет `duration_seconds = (ended - started).total_seconds()`.
3. Устанавливает `closed = True`.
4. Обновляет `DailyAttendance`.

**Шаг 5 — Пересчёт DailyAttendance**

После закрытия сессии `_update_daily_attendance(work_session)` пересчитывает весь день заново:

```
total_work_seconds    = Σ duration_seconds всех закрытых сессий за день
planned_seconds       = to_time - from_time из EmployeeWorkDay
late_seconds          = max(0, первая_сессия.started - planned_from_time)
early_leave_seconds   = max(0, planned_to_time - последняя_сессия.ended)
overtime_seconds      = max(0, последняя_сессия.ended - planned_to_time)
```

### 5.2 Алгоритм расчёта зарплаты

Функция `calculate_employee_payroll(employee, period)`:

**Для почасовой ставки (HOURLY):**
```
base_amount      = (total_work_seconds / 3600) × hourly_rate
overtime_amount  = (overtime_seconds / 3600) × hourly_rate × 1.0
penalty_amount   = ((late_seconds + early_leave_seconds) / 3600) × hourly_rate
total_amount     = base_amount + overtime_amount - penalty_amount
```

**Для ежемесячной ставки (MONTHLY):**
```
base_amount      = monthly_amount  (фиксированная сумма)
overtime_amount  = (overtime_seconds / 3600) × (monthly_amount / planned_hours) × 1.0
penalty_amount   = ((late_seconds + early_leave_seconds) / 3600) × (monthly_amount / planned_hours)
total_amount     = base_amount + overtime_amount - penalty_amount
```

Каждая из этих составляющих записывается как отдельная позиция `PayrollItem` с соответствующим `type`.

### 5.3 Алгоритм дашборда и генерация алертов

`get_dashboard_data(user)` формирует ответ со следующими вычислениями:

```
today_present_percent = (today_present / total_employees) × 100
today_late_percent    = (today_late / today_present) × 100

today_present_change_percent = percent_change(today_present, yesterday_present)
today_late_change_percent    = percent_change(today_late, yesterday_late)
```

**Автоматические алерты:**
- `LATE_SPIKE` — генерируется, если количество опозданий сегодня выросло более чем на 30% по сравнению с вчера.
- `LOW_ATTENDANCE` — генерируется, если посещаемость сегодня ниже 70%.

---

## 6. API документация

### 6.1 Аутентификация

Все API-эндпоинты (кроме получения токена) требуют JWT-аутентификацию.

| Метод | Эндпоинт | Описание |
|---|---|---|
| POST | `/api/token/` | Получение пары токенов access/refresh |
| POST | `/api/token/refresh/` | Обновление access токена |
| POST | `/api/token/verify/` | Верификация токена |

**Пример запроса:**
```http
POST /api/token/
Content-Type: application/json

{
  "username": "admin",
  "password": "password123"
}
```

**Пример ответа:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Полученный `access` токен передаётся в заголовке:
```
Authorization: Bearer <access_token>
```

Access токен действителен **5 минут**, refresh токен — **1 день**.

---

### 6.2 Предприятие и отделы `/api/v1/enterprise/`

#### GET `/api/v1/enterprise/enterprise/`
Возвращает данные предприятия текущего пользователя.

**Ответ:**
```json
{
  "id": 1,
  "name": "ООО Пример",
  "code": "ENT-1234567890",
  "departments_count": 5,
  "employees_count": 120
}
```

#### GET `/api/v1/enterprise/departments/`
Список корневых отделов предприятия с подотделами и количеством сотрудников.

**Ответ:**
```json
[
  {
    "id": 1,
    "name": "IT отдел",
    "code": "DEP-0000000001",
    "employees_count": 15,
    "children": [
      {
        "id": 3,
        "name": "Backend",
        "employees_count": 8,
        "children": []
      }
    ]
  }
]
```

#### POST `/api/v1/enterprise/departments/create/`
Создание нового отдела.

**Тело запроса:**
```json
{
  "name": "Новый отдел",
  "parent": 1
}
```

#### GET `/api/v1/enterprise/departments/<id>/`
Детальная информация об отделе с иерархией подотделов.

---

### 6.3 Сотрудники `/api/v1/employees/`

#### POST `/api/v1/employees/create/`
Создание нового сотрудника с компенсацией и графиком работы.

**Тело запроса:**
```json
{
  "department": 2,
  "first_name": "Иван",
  "last_name": "Иванов",
  "middle_name": "Иванович",
  "code": "EMP-001",
  "detail": {
    "salary_type": "HOURLY",
    "amount": "10000.00",
    "effective_from": "2026-01-01",
    "work_days": [
      {"weekday": 0, "from_time": "08:30", "to_time": "18:30"},
      {"weekday": 1, "from_time": "08:30", "to_time": "18:30"},
      {"weekday": 2, "from_time": "08:30", "to_time": "18:30"},
      {"weekday": 3, "from_time": "08:30", "to_time": "18:30"},
      {"weekday": 4, "from_time": "08:30", "to_time": "18:30"}
    ]
  }
}
```

#### POST `/api/v1/employees/search/`
Поиск сотрудника по табельному номеру или ФИО.

**Поиск по коду:**
```json
{ "code": "EMP-001" }
```

**Поиск по имени:**
```json
{
  "first_name": "Иван",
  "last_name": "Иванов",
  "middle_name": "Иванович"
}
```

#### GET `/api/v1/employees/employees/`
Список всех сотрудников предприятия.

#### GET `/api/v1/employees/employees/<id>/`
Детальная информация о сотруднике (включая текущий график и компенсацию).

#### PATCH `/api/v1/employees/employees/<id>/update/`
Обновление компенсации и графика работы сотрудника.

```json
{
  "salary_type": "MONTHLY",
  "amount": "150000.00",
  "effective_from": "2026-04-01",
  "work_days": [
    {"weekday": 0, "from_time": "09:00", "to_time": "18:00"},
    {"weekday": 1, "from_time": "09:00", "to_time": "18:00"},
    {"weekday": 2, "from_time": "09:00", "to_time": "18:00"},
    {"weekday": 3, "from_time": "09:00", "to_time": "18:00"},
    {"weekday": 4, "from_time": "09:00", "to_time": "18:00"}
  ]
}
```

---

### 6.4 Контроль доступа `/api/v1/access-controls/`

#### POST `/api/v1/access-controls/create/`
Регистрация события доступа (вход или выход сотрудника).

**Тело запроса:**
```json
{
  "employee": 5,
  "timestamp": "2026-04-01T08:35:00Z",
  "type": "ENTER"
}
```

**Типы событий:**
- `ENTER` — вход на предприятие
- `LEAVE` — выход с предприятия

После создания автоматически запускается Celery-задача обработки рабочей сессии.

#### GET `/api/v1/access-controls/work-sessions/`
Список рабочих сессий сотрудников предприятия.

**Параметры фильтрации:**
- `employee` — ID сотрудника
- `closed` — true/false

#### GET `/api/v1/access-controls/daily-attendances/`
Список ежедневных записей о посещаемости.

**Параметры фильтрации:**
- `employee` — ID сотрудника
- `date` — дата в формате YYYY-MM-DD
- `search` — поиск по имени сотрудника

**Пример ответа:**
```json
[
  {
    "id": 1,
    "employee": "Иванов Иван Иванович",
    "date": "2026-04-01",
    "work_seconds": 32400,
    "late_seconds": 300,
    "planned_seconds": 36000,
    "overtime_seconds": 0,
    "early_leave_seconds": 3600
  }
]
```

---

### 6.5 Расчёт зарплаты `/api/v1/payroll-periods/`

#### GET `/api/v1/payroll-periods/`
Список всех периодов расчёта зарплаты.

#### POST `/api/v1/payroll-periods/create/`
Создание нового периода выплаты.

```json
{
  "start_date": "2026-04-01",
  "end_date": "2026-04-30"
}
```

#### POST `/api/v1/payroll-periods/<id>/recalculate/`
Запуск асинхронного пересчёта зарплаты для всех сотрудников в периоде. Задача выполняется в фоне через Celery.

#### GET `/api/v1/payroll-periods/<id>/employees/`
Список рассчитанных зарплат всех сотрудников за период.

**Пример ответа:**
```json
[
  {
    "id": 10,
    "employee": "Иванов Иван Иванович",
    "total_work_seconds": 576000,
    "total_amount": "95000.00",
    "is_finalized": false,
    "items": [
      {"type": "BASE", "amount": "100000.00", "description": "Базовая зарплата"},
      {"type": "PENALTY", "amount": "5000.00", "description": "Штраф за опоздания"}
    ]
  }
]
```

#### GET `/api/v1/payroll-periods/employee-payrolls/<id>/`
Детальная информация о зарплате конкретного сотрудника.

#### POST `/api/v1/payroll-periods/employee-payrolls/<id>/finalize/`
Подтверждение (финализация) зарплаты одного сотрудника. После финализации изменения невозможны.

#### POST `/api/v1/payroll-periods/employee-payrolls/finalize/`
Массовая финализация нескольких зарплат.

```json
{
  "payroll_ids": [10, 11, 12, 13]
}
```

---

### 6.6 Дашборд `/api/v1/dashboard/`

#### GET `/api/v1/dashboard/`
Сводная информация о состоянии предприятия на текущий день.

**Пример ответа:**
```json
{
  "summary": {
    "total_employees": 120,
    "total_departments": 8,
    "today_present": 98,
    "today_present_percent": 81.67,
    "today_present_change_percent": 3.2,
    "today_late": 12,
    "today_late_percent": 12.24,
    "today_late_change_percent": -5.1
  },
  "series": {
    "activity_7_days": [
      {
        "date": "2026-03-26",
        "present_count": 95,
        "total_work_seconds": 3420000,
        "total_late_seconds": 18000
      }
    ]
  },
  "alerts": [
    {
      "level": "warning",
      "code": "LATE_SPIKE",
      "message": "Количество опозданий выросло более чем на 30%"
    }
  ],
  "meta": {
    "as_of": "2026-04-01",
    "timezone": "UTC"
  }
}
```

**Возможные алерты:**

| Код алерта | Уровень | Условие срабатывания |
|---|---|---|
| `LATE_SPIKE` | warning | Опоздания выросли более чем на 30% по сравнению с вчера |
| `LOW_ATTENDANCE` | warning | Посещаемость сегодня ниже 70% |

---

## 7. Асинхронные задачи Celery

### 7.1 Конфигурация Celery

```python
# src/celery_app.py
app = Celery("access_control_system")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
```

Брокер и backend: **Redis**. Сериализация: **JSON**. Лимиты: мягкий 60 сек, жёсткий 5 минут.

### 7.2 Задача обработки рабочей сессии

```
processing_work_session(access_event_id: int)
```

- **Модуль:** `apps.access_control.tasks`
- **Повторные попытки:** 3 раза с задержкой 5 секунд
- **Механизм:** `select_for_update()` для защиты от race conditions
- **Запуск:** автоматически через Django-сигнал при создании `AccessEvent`

### 7.3 Задачи расчёта зарплаты

```
recalculate_payroll_period_task(enterprise_id, period_id)
recalculate_employee_payroll_task(employee_id, period_id, force_recalculate=True)
```

- **Модуль:** `apps.payroll.tasks`
- **Повторные попытки:** 3 раза с задержкой 5 секунд
- `recalculate_payroll_period_task` — запускает индивидуальные задачи для каждого сотрудника (PostgreSQL: параллельно, SQLite: последовательно)

---

## 8. Развёртывание и настройка

### 8.1 Переменные окружения

| Переменная | Описание | Пример |
|---|---|---|
| `SECRET_KEY` | Django секретный ключ | `django-insecure-...` |
| `DEBUG` | Режим отладки | `True` / `False` |
| `DB_TYPE` | Тип БД | `postgres` / `sqlite` |
| `DB_HOST` | Хост базы данных | `localhost` |
| `DB_PORT` | Порт БД | `5432` |
| `DB_NAME` | Имя БД | `access_control_db` |
| `DB_USER` | Пользователь БД | `postgres` |
| `DB_PASSWORD` | Пароль БД | `secret` |
| `CELERY_BROKER_URL` | URL брокера Redis | `redis://localhost:6379/0` |
| `REDIS_HOST` | Хост Redis | `localhost` |
| `REDIS_PORT` | Порт Redis | `6379` |

### 8.2 Установка и запуск (разработка)

```bash
# 1. Клонирование репозитория
git clone <repo-url>
cd access-control-system

# 2. Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# 3. Установка зависимостей
pip install -r requirements/base.txt

# 4. Применение миграций
python manage.py migrate

# 5. Создание суперпользователя
python manage.py createsuperuser

# 6. Запуск Django сервера
python manage.py runserver

# 7. Запуск Celery воркера (в отдельном терминале)
celery -A src.celery_app worker --loglevel=info

# 8. Запуск Celery beat (в отдельном терминале)
celery -A src.celery_app beat --loglevel=info
```

### 8.3 Первоначальное заполнение данными

```bash
# Создать предприятие с 3 отделами и 2 подотделами
python manage.py create_ent --dep 3 --part 2

# Создать 10 сотрудников для предприятия с ID=1
python manage.py create_employees --id 1 --count 10

# Сгенерировать тестовые события доступа за март 2026
python manage.py create_access_control --id 1
```

---

## 9. Управляющие команды

### `create_ent` — Создание предприятия

```bash
python manage.py create_ent [--dep N] [--part N]
```

| Параметр | По умолчанию | Описание |
|---|---|---|
| `--dep` | 1 | Количество корневых отделов |
| `--part` | 1 | Количество подотделов в каждом отделе |

Команда создаёт Enterprise, связанные Department'ы и PayrollPeriod (Январь 2026) для владельца с `user_id=1`.

### `create_employees` — Создание сотрудников

```bash
python manage.py create_employees --id <enterprise_id> [--count N]
```

| Параметр | По умолчанию | Описание |
|---|---|---|
| `--id` | обязателен | ID предприятия |
| `--count` | 5 | Сотрудников на каждый отдел |

Каждый сотрудник создаётся с графиком Пн–Пт, 08:30–18:30, случайная почасовая ставка 5 000–15 000.

### `create_access_control` — Генерация событий

```bash
python manage.py create_access_control --id <enterprise_id>
```

Создаёт события за март 2026 для всех сотрудников предприятия. По 4 события в день (вход, перерыв, возврат, выход) в рабочие дни.

---

## 10. Рабочие процессы системы

### 10.1 Полный цикл учёта рабочего времени

```
Турникет/устройство
       │
       ▼
POST /api/v1/access-controls/create/
       │
       ▼
AccessEvent сохранён в БД
       │
  Django Signal
       │
       ▼
processing_work_session.delay(event_id) → Redis Queue
       │
       ▼
Celery Worker обрабатывает:
  ├── ENTER → закрыть старую сессию + открыть новую
  └── LEAVE → закрыть текущую сессию
       │
       ▼
_update_daily_attendance() → обновить DailyAttendance
```

### 10.2 Цикл расчёта заработной платы

```
Администратор
       │
       ▼
POST /api/v1/payroll-periods/create/
       │
       ▼
POST /api/v1/payroll-periods/<id>/recalculate/
       │
       ▼
recalculate_payroll_period_task → Redis Queue
       │
       ▼
Для каждого сотрудника: recalculate_employee_payroll_task
       │
       ▼
calculate_employee_payroll():
  ├── Получить DailyAttendance за период
  ├── Рассчитать BASE / OVERTIME / PENALTY
  └── Сохранить EmployeePayroll + PayrollItems
       │
       ▼
POST /api/v1/payroll-periods/employee-payrolls/<id>/finalize/
```

### 10.3 Обновление компенсации сотрудника

```
Менеджер HR
       │
       ▼
PATCH /api/v1/employees/employees/<id>/update/
       │
       ▼
update_employee_compensation() (atomic transaction):
  ├── Деактивировать старый EmployeeDetail (is_active=False)
  ├── Создать новый EmployeeDetail (is_active=True)
  └── Создать EmployeeWorkDay записи
```

---

## Дополнительные ресурсы

- **Swagger UI:** `/api/schema/swagger-ui/` (при включённом drf-spectacular)
- **ReDoc:** `/api/schema/redoc/`
- **Django Admin:** `/admin/` (с интерфейсом django-unfold)

---

*Документ подготовлен для версии 1.0.1 проекта Access Control System*
