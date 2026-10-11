"""Generate DOCUMENTATION.docx from markdown content."""

from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy

doc = Document()

# --- Page margins ---
for section in doc.sections:
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2)

# --- Styles ---
styles = doc.styles

normal = styles['Normal']
normal.font.name = 'Times New Roman'
normal.font.size = Pt(12)

h1_style = styles['Heading 1']
h1_style.font.name = 'Times New Roman'
h1_style.font.size = Pt(18)
h1_style.font.bold = True
h1_style.font.color.rgb = RGBColor(0x1a, 0x56, 0x9e)

h2_style = styles['Heading 2']
h2_style.font.name = 'Times New Roman'
h2_style.font.size = Pt(15)
h2_style.font.bold = True
h2_style.font.color.rgb = RGBColor(0x1a, 0x56, 0x9e)

h3_style = styles['Heading 3']
h3_style.font.name = 'Times New Roman'
h3_style.font.size = Pt(13)
h3_style.font.bold = True
h3_style.font.color.rgb = RGBColor(0x2e, 0x75, 0xb6)

# --- Helper to set paragraph border ---
def add_shading(paragraph, fill="F2F2F2"):
    pPr = paragraph._p.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill)
    pPr.append(shd)

def add_paragraph(text, style='Normal', bold=False, size=None, color=None, align=None):
    p = doc.add_paragraph(style=style)
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    if bold:
        run.bold = True
    if size:
        run.font.size = Pt(size)
    if color:
        run.font.color.rgb = RGBColor(*color)
    if align:
        p.alignment = align
    return p

def add_code_block(lines):
    for line in lines:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(0.5)
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(line)
        run.font.name = 'Courier New'
        run.font.size = Pt(9)
        add_shading(p, "F0F0F0")

def add_table(headers, rows):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].text = h
        for run in hdr_cells[i].paragraphs[0].runs:
            run.font.bold = True
            run.font.name = 'Times New Roman'
            run.font.size = Pt(10)
        tc = hdr_cells[i]._tc
        tcPr = tc.get_or_add_tcPr()
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'), 'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'), '1A569E')
        tcPr.append(shd)
        for p in hdr_cells[i].paragraphs:
            for run in p.runs:
                run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    for row_data in rows:
        row = table.add_row()
        for i, cell_text in enumerate(row_data):
            row.cells[i].text = cell_text
            for p in row.cells[i].paragraphs:
                for run in p.runs:
                    run.font.name = 'Times New Roman'
                    run.font.size = Pt(10)
    doc.add_paragraph()

# =============================================
# TITLE PAGE
# =============================================
doc.add_paragraph()
doc.add_paragraph()
doc.add_paragraph()

title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = title.add_run('СИСТЕМА КОНТРОЛЯ ДОСТУПА\nAccess Control System')
run.font.name = 'Times New Roman'
run.font.size = Pt(24)
run.font.bold = True
run.font.color.rgb = RGBColor(0x1a, 0x56, 0x9e)

doc.add_paragraph()

subtitle = doc.add_paragraph()
subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
run2 = subtitle.add_run('Техническая документация')
run2.font.name = 'Times New Roman'
run2.font.size = Pt(16)
run2.font.color.rgb = RGBColor(0x44, 0x44, 0x44)

doc.add_paragraph()
doc.add_paragraph()

meta = doc.add_paragraph()
meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
meta.add_run('Версия: 1.0.1\n').font.name = 'Times New Roman'
meta.runs[-1].font.size = Pt(12)
meta.add_run('Дата: 2026-04-01\n').font.name = 'Times New Roman'
meta.runs[-1].font.size = Pt(12)
meta.add_run('Автор: ChoriyevJamshid').font.name = 'Times New Roman'
meta.runs[-1].font.size = Pt(12)

doc.add_page_break()

# =============================================
# 1. OVERVIEW
# =============================================
doc.add_heading('1. Обзор проекта', level=1)
add_paragraph(
    'Access Control System — многофункциональная серверная система для управления контролем доступа '
    'сотрудников на предприятии. Система предоставляет полный цикл: от регистрации событий прохода '
    'через турникет до расчёта заработной платы с учётом опозданий и переработок.',
    size=12
)
doc.add_paragraph()
add_paragraph('Основные возможности системы:', bold=True)

features = [
    'Учёт рабочего времени — фиксация событий входа/выхода, автоматическое формирование рабочих сессий и ежедневной посещаемости.',
    'Управление персоналом — создание и ведение базы сотрудников с историей компенсаций и графиков работы.',
    'Расчёт заработной платы — автоматический расчёт на основе фактически отработанного времени (почасовая и ежемесячная системы).',
    'Аналитический дашборд — сводная информация, статистика за 7 дней, автоматические предупреждения.',
    'Управление предприятием — иерархическая структура отделов, мультиуровневая организация.',
]
for f in features:
    p = doc.add_paragraph(style='List Bullet')
    run = p.add_run(f)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)

doc.add_paragraph()
add_paragraph(
    'Архитектура системы построена на принципах чистого кода с чётким разделением ответственности: '
    'Models → Selectors → Services → Serializers → Views.',
    size=12
)

# =============================================
# 2. TECH STACK
# =============================================
doc.add_heading('2. Технологический стек', level=1)

doc.add_heading('2.1 Основной фреймворк', level=2)
add_table(
    ['Технология', 'Версия', 'Назначение'],
    [
        ['Python', '3.12+', 'Язык программирования'],
        ['Django', '5.2', 'Основной веб-фреймворк'],
        ['Django REST Framework', '3.16.1', 'Создание REST API'],
        ['djangorestframework-simplejwt', '5.5.1', 'JWT аутентификация'],
    ]
)

doc.add_heading('2.2 База данных', level=2)
add_table(
    ['Технология', 'Версия', 'Назначение'],
    [
        ['PostgreSQL', '14+', 'Основная СУБД (production)'],
        ['SQLite', 'встроенная', 'СУБД для разработки'],
        ['PgBouncer', '—', 'Пул соединений к PostgreSQL'],
    ]
)

doc.add_heading('2.3 Очередь задач и кэш', level=2)
add_table(
    ['Технология', 'Версия', 'Назначение'],
    [
        ['Celery', '5.6.2', 'Асинхронная очередь задач'],
        ['django-celery-beat', '2.8.1', 'Периодические задачи (cron)'],
        ['Redis', '7.2.0', 'Брокер сообщений и backend результатов'],
        ['django-redis', '6.0.0', 'Кэширование на базе Redis'],
    ]
)

doc.add_heading('2.4 Безопасность и API', level=2)
add_table(
    ['Технология', 'Версия', 'Назначение'],
    [
        ['django-allauth', '65.14.3', 'Аутентификация и управление аккаунтами'],
        ['argon2-cffi', '25.1.0', 'Хэширование паролей (Argon2)'],
        ['django-cors-headers', '4.9.0', 'CORS политика'],
        ['drf-spectacular', '0.29.0', 'OpenAPI / Swagger документация'],
        ['whitenoise', '6.11.1', 'Раздача статических файлов'],
    ]
)

doc.add_heading('2.5 Инфраструктура', level=2)
add_table(
    ['Технология', 'Версия', 'Назначение'],
    [
        ['Django Channels', '4.3.2', 'WebSocket / асинхронная поддержка'],
        ['gunicorn', '25.1.0', 'WSGI сервер для production'],
        ['uvicorn', '0.41.0', 'ASGI сервер'],
        ['django-unfold', '0.66.0', 'Современный интерфейс Django Admin'],
        ['django-filter', '25.2', 'Фильтрация в API'],
    ]
)

# =============================================
# 3. ARCHITECTURE
# =============================================
doc.add_heading('3. Архитектура системы', level=1)

doc.add_heading('3.1 Структура проекта', level=2)
add_code_block([
    'access-control-system/',
    '├── apps/                       # Django приложения',
    '│   ├── base_models.py          # Абстрактная BaseModel (created/updated)',
    '│   ├── users/                  # Пользователи, предприятия, отделы',
    '│   ├── employees/              # Сотрудники, компенсации, графики',
    '│   ├── access_control/         # События доступа, сессии, посещаемость',
    '│   └── payroll/                # Расчёт зарплаты, периоды выплат',
    '├── api/',
    '│   ├── urls.py                 # JWT токены',
    '│   └── v1/',
    '│       ├── access_control/     # Эндпоинты контроля доступа',
    '│       ├── employees/          # Эндпоинты сотрудников',
    '│       ├── enterprise/         # Эндпоинты предприятия / отделов',
    '│       ├── dashboard/          # Эндпоинт дашборда',
    '│       └── payroll/            # Эндпоинты зарплаты',
    '├── src/',
    '│   ├── settings/base.py        # Основная конфигурация',
    '│   ├── urls.py                 # Корневая маршрутизация',
    '│   └── celery_app.py           # Конфигурация Celery',
    '└── requirements/base.txt       # Зависимости',
])
doc.add_paragraph()

doc.add_heading('3.2 Применяемые паттерны', level=2)

patterns = [
    ('Service Layer (Сервисный слой)', 'Вся бизнес-логика инкапсулирована в файлах services.py. Views не содержат бизнес-логики — только вызовы сервисов.'),
    ('Selector Pattern (Паттерн селекторов)', 'Сложные запросы к БД вынесены в selectors.py. Это обеспечивает переиспользование и изоляцию доступа к данным.'),
    ('Signal-driven Architecture', 'При сохранении AccessEvent Django-сигнал автоматически запускает Celery-задачу. Обеспечивает асинхронность и слабую связность.'),
    ('Abstract Base Model', 'Все модели наследуются от BaseModel с полями created и updated (auto_now_add / auto_now).'),
]
for name, desc in patterns:
    p = doc.add_paragraph()
    run = p.add_run(f'{name}: ')
    run.bold = True
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run2 = p.add_run(desc)
    run2.font.name = 'Times New Roman'
    run2.font.size = Pt(12)

# =============================================
# 4. DATA MODELS
# =============================================
doc.add_heading('4. Модели данных', level=1)

doc.add_heading('4.1 Предприятие (Enterprise)', level=2)
add_table(
    ['Поле', 'Тип', 'Описание'],
    [
        ['name', 'CharField(63)', 'Название предприятия'],
        ['code', 'CharField (unique)', 'Уникальный код "ENT-XXXXXXXXXX" (авто)'],
        ['owner', 'OneToOneField → User', 'Владелец предприятия'],
    ]
)

doc.add_heading('4.2 Отдел (Department)', level=2)
add_table(
    ['Поле', 'Тип', 'Описание'],
    [
        ['name', 'CharField(63)', 'Название отдела'],
        ['code', 'CharField (unique)', 'Уникальный код "DEP-XXXXXXXXXX" (авто)'],
        ['enterprise', 'ForeignKey → Enterprise', 'Принадлежность к предприятию'],
        ['parent', 'ForeignKey → self (null)', 'Родительский отдел (иерархия)'],
    ]
)

doc.add_heading('4.3 Сотрудник (Employee)', level=2)
add_table(
    ['Поле', 'Тип', 'Описание'],
    [
        ['enterprise', 'ForeignKey → Enterprise', 'Предприятие'],
        ['department', 'ForeignKey → Department', 'Отдел'],
        ['first_name', 'CharField(31)', 'Имя'],
        ['last_name', 'CharField(31)', 'Фамилия'],
        ['middle_name', 'CharField(31)', 'Отчество'],
        ['code', 'CharField(63)', 'Табельный номер (уникален в предприятии)'],
    ]
)

doc.add_heading('4.4 Компенсация сотрудника (EmployeeDetail)', level=2)
add_table(
    ['Поле', 'Тип', 'Описание'],
    [
        ['employee', 'ForeignKey → Employee', 'Сотрудник'],
        ['salary_type', 'CharField choices', 'HOURLY (почасовой) / MONTHLY (ежемесячный)'],
        ['amount', 'DecimalField(14,2)', 'Сумма компенсации'],
        ['effective_from', 'DateField', 'Дата начала действия'],
        ['effective_to', 'DateField (null)', 'Дата окончания (null = действует)'],
        ['is_active', 'BooleanField', 'Активна ли запись (только одна = True)'],
    ]
)

doc.add_heading('4.5 График работы (EmployeeWorkDay)', level=2)
add_table(
    ['Поле', 'Тип', 'Описание'],
    [
        ['detail', 'ForeignKey → EmployeeDetail', 'Запись компенсации'],
        ['weekday', 'PositiveSmallInt (0–6)', 'День недели (0=Пн, 6=Вс)'],
        ['from_time', 'TimeField', 'Начало рабочего дня'],
        ['to_time', 'TimeField', 'Конец рабочего дня'],
        ['hours', 'DurationField', 'Плановое количество часов'],
    ]
)

doc.add_heading('4.6 Событие доступа (AccessEvent)', level=2)
add_table(
    ['Поле', 'Тип', 'Описание'],
    [
        ['employee', 'ForeignKey → Employee', 'Сотрудник'],
        ['timestamp', 'DateTimeField (indexed)', 'Время события'],
        ['type', 'CharField choices', 'ENTER (вход) / LEAVE (выход)'],
    ]
)
add_paragraph('При создании сигнал post_save автоматически запускает Celery-задачу processing_work_session.', size=11)

doc.add_heading('4.7 Рабочая сессия (WorkSession)', level=2)
add_table(
    ['Поле', 'Тип', 'Описание'],
    [
        ['employee', 'ForeignKey → Employee', 'Сотрудник'],
        ['started', 'DateTimeField', 'Начало сессии'],
        ['ended', 'DateTimeField (null)', 'Конец сессии'],
        ['duration_seconds', 'PositiveIntegerField (null)', 'Длительность в секундах'],
        ['closed', 'BooleanField', 'Закрыта ли сессия'],
    ]
)

doc.add_heading('4.8 Ежедневная посещаемость (DailyAttendance)', level=2)
add_table(
    ['Поле', 'Тип', 'Описание'],
    [
        ['employee', 'ForeignKey → Employee', 'Сотрудник'],
        ['date', 'DateField (indexed)', 'Дата'],
        ['work_seconds', 'PositiveIntegerField', 'Фактически отработанные секунды'],
        ['late_seconds', 'PositiveIntegerField', 'Секунды опоздания'],
        ['planned_seconds', 'PositiveIntegerField', 'Плановые секунды'],
        ['overtime_seconds', 'PositiveIntegerField', 'Переработка в секундах'],
        ['early_leave_seconds', 'PositiveIntegerField', 'Ранний уход в секундах'],
    ]
)

doc.add_heading('4.9 Модели расчёта зарплаты', level=2)
add_paragraph('PayrollPeriod (Период выплаты):', bold=True)
add_table(
    ['Поле', 'Тип', 'Описание'],
    [
        ['start_date', 'DateField', 'Начало периода'],
        ['end_date', 'DateField', 'Конец периода'],
        ['is_closed', 'BooleanField', 'Закрыт ли период'],
    ]
)

add_paragraph('EmployeePayroll (Зарплата сотрудника за период):', bold=True)
add_table(
    ['Поле', 'Тип', 'Описание'],
    [
        ['employee', 'ForeignKey → Employee', 'Сотрудник'],
        ['period', 'ForeignKey → PayrollPeriod', 'Период расчёта'],
        ['total_work_seconds', 'PositiveIntegerField', 'Итого отработанных секунд'],
        ['total_amount', 'DecimalField(14,2)', 'Итоговая сумма зарплаты'],
        ['calculated_at', 'DateTimeField (auto_now)', 'Дата расчёта'],
        ['is_finalized', 'BooleanField', 'Подтверждён ли расчёт'],
    ]
)

add_paragraph('PayrollItem (Позиция зарплатного расчёта):', bold=True)
add_table(
    ['Поле', 'Тип', 'Описание'],
    [
        ['payroll', 'ForeignKey → EmployeePayroll', 'Зарплата'],
        ['type', 'CharField choices', 'BASE / OVERTIME / BONUS / PENALTY / MANUAL'],
        ['amount', 'DecimalField(14,2)', 'Сумма позиции'],
        ['description', 'CharField(255)', 'Описание позиции'],
    ]
)

# =============================================
# 5. BUSINESS LOGIC
# =============================================
doc.add_heading('5. Бизнес-логика и алгоритмы', level=1)

doc.add_heading('5.1 Алгоритм обработки события доступа', level=2)
steps = [
    ('Шаг 1 — Проверка дубликатов', 'check_access_exists_service(employee, timestamp, type) — проверяет наличие уже зарегистрированного аналогичного события.'),
    ('Шаг 2 — Запуск задачи', 'Django-сигнал post_save вызывает processing_work_session.delay(access_event_id) для асинхронной обработки.'),
    ('Шаг 3 — Обработка ENTER', 'Проверяет плановый рабочий день. Закрывает предыдущую открытую сессию (если есть). Создаёт новую WorkSession.'),
    ('Шаг 4 — Обработка LEAVE', 'Находит открытую WorkSession. Устанавливает ended и duration_seconds. Закрывает сессию (closed=True).'),
    ('Шаг 5 — Пересчёт посещаемости', '_update_daily_attendance() пересчитывает весь DailyAttendance за день заново.'),
]
for title, desc in steps:
    p = doc.add_paragraph()
    run = p.add_run(f'{title}: ')
    run.bold = True
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run2 = p.add_run(desc)
    run2.font.name = 'Times New Roman'
    run2.font.size = Pt(12)

doc.add_paragraph()
add_paragraph('Формулы расчёта DailyAttendance:', bold=True)
add_code_block([
    'total_work_seconds    = Σ duration_seconds всех закрытых сессий за день',
    'planned_seconds       = to_time - from_time из EmployeeWorkDay',
    'late_seconds          = max(0, первая_сессия.started - planned_from_time)',
    'early_leave_seconds   = max(0, planned_to_time - последняя_сессия.ended)',
    'overtime_seconds      = max(0, последняя_сессия.ended - planned_to_time)',
])

doc.add_heading('5.2 Алгоритм расчёта заработной платы', level=2)
add_paragraph('Для почасовой ставки (HOURLY):', bold=True)
add_code_block([
    'base_amount      = (total_work_seconds / 3600) × hourly_rate',
    'overtime_amount  = (overtime_seconds / 3600) × hourly_rate × 1.0',
    'penalty_amount   = ((late_seconds + early_leave_seconds) / 3600) × hourly_rate',
    'total_amount     = base_amount + overtime_amount - penalty_amount',
])
doc.add_paragraph()
add_paragraph('Для ежемесячной ставки (MONTHLY):', bold=True)
add_code_block([
    'hourly_rate      = monthly_amount / planned_hours',
    'base_amount      = monthly_amount (фиксированная сумма)',
    'overtime_amount  = (overtime_seconds / 3600) × hourly_rate × 1.0',
    'penalty_amount   = ((late_seconds + early_leave_seconds) / 3600) × hourly_rate',
    'total_amount     = base_amount + overtime_amount - penalty_amount',
])
doc.add_paragraph()
add_paragraph(
    'Каждая составляющая записывается как отдельная позиция PayrollItem с соответствующим типом (BASE, OVERTIME, PENALTY).',
    size=12
)

doc.add_heading('5.3 Алгоритм формирования дашборда', level=2)
add_code_block([
    'today_present_percent        = (today_present / total_employees) × 100',
    'today_late_percent           = (today_late / today_present) × 100',
    'today_present_change_percent = percent_change(today_present, yesterday_present)',
    'today_late_change_percent    = percent_change(today_late, yesterday_late)',
])
doc.add_paragraph()
add_paragraph('Автоматические алерты:', bold=True)
add_table(
    ['Код алерта', 'Уровень', 'Условие срабатывания'],
    [
        ['LATE_SPIKE', 'warning', 'Опоздания выросли более чем на 30% по сравнению с вчера'],
        ['LOW_ATTENDANCE', 'warning', 'Посещаемость сегодня ниже 70%'],
    ]
)

# =============================================
# 6. API DOCUMENTATION
# =============================================
doc.add_heading('6. API документация', level=1)

doc.add_heading('6.1 Аутентификация', level=2)
add_paragraph(
    'Все API-эндпоинты требуют JWT-аутентификацию. Токен передаётся в заголовке: Authorization: Bearer <access_token>. '
    'Access токен действителен 5 минут, refresh токен — 1 день.',
    size=12
)
add_table(
    ['Метод', 'Эндпоинт', 'Описание'],
    [
        ['POST', '/api/token/', 'Получение пары токенов access/refresh'],
        ['POST', '/api/token/refresh/', 'Обновление access токена по refresh токену'],
        ['POST', '/api/token/verify/', 'Верификация access токена'],
    ]
)

doc.add_heading('6.2 Предприятие и отделы  /api/v1/enterprise/', level=2)
add_table(
    ['Метод', 'Эндпоинт', 'Описание'],
    [
        ['GET', '/api/v1/enterprise/enterprise/', 'Данные предприятия текущего пользователя'],
        ['GET', '/api/v1/enterprise/departments/', 'Список корневых отделов с подотделами'],
        ['POST', '/api/v1/enterprise/departments/create/', 'Создание нового отдела'],
        ['GET', '/api/v1/enterprise/departments/<id>/', 'Детальная информация об отделе'],
    ]
)

doc.add_heading('6.3 Сотрудники  /api/v1/employees/', level=2)
add_table(
    ['Метод', 'Эндпоинт', 'Описание'],
    [
        ['POST', '/api/v1/employees/create/', 'Создание сотрудника с компенсацией и графиком'],
        ['POST', '/api/v1/employees/search/', 'Поиск сотрудника по коду или ФИО'],
        ['GET', '/api/v1/employees/employees/', 'Список всех сотрудников предприятия'],
        ['GET', '/api/v1/employees/employees/<id>/', 'Детальная информация о сотруднике'],
        ['PATCH', '/api/v1/employees/employees/<id>/update/', 'Обновление компенсации и графика'],
    ]
)

add_paragraph('Пример создания сотрудника (POST /api/v1/employees/create/):', bold=True)
add_code_block([
    '{',
    '  "department": 2,',
    '  "first_name": "Иван",',
    '  "last_name": "Иванов",',
    '  "middle_name": "Иванович",',
    '  "code": "EMP-001",',
    '  "detail": {',
    '    "salary_type": "HOURLY",',
    '    "amount": "10000.00",',
    '    "effective_from": "2026-01-01",',
    '    "work_days": [',
    '      {"weekday": 0, "from_time": "08:30", "to_time": "18:30"},',
    '      {"weekday": 1, "from_time": "08:30", "to_time": "18:30"},',
    '      {"weekday": 2, "from_time": "08:30", "to_time": "18:30"},',
    '      {"weekday": 3, "from_time": "08:30", "to_time": "18:30"},',
    '      {"weekday": 4, "from_time": "08:30", "to_time": "18:30"}',
    '    ]',
    '  }',
    '}',
])

doc.add_heading('6.4 Контроль доступа  /api/v1/access-controls/', level=2)
add_table(
    ['Метод', 'Эндпоинт', 'Описание'],
    [
        ['POST', '/api/v1/access-controls/create/', 'Регистрация события входа/выхода'],
        ['GET', '/api/v1/access-controls/work-sessions/', 'Список рабочих сессий сотрудников'],
        ['GET', '/api/v1/access-controls/daily-attendances/', 'Список ежедневной посещаемости'],
    ]
)
add_paragraph('Пример регистрации события (POST /api/v1/access-controls/create/):', bold=True)
add_code_block([
    '{',
    '  "employee": 5,',
    '  "timestamp": "2026-04-01T08:35:00Z",',
    '  "type": "ENTER"',
    '}',
])
add_paragraph('Допустимые значения поля type: ENTER (вход), LEAVE (выход).', size=11)
add_paragraph(
    'Параметры фильтрации для daily-attendances: employee (ID), date (YYYY-MM-DD), search (имя сотрудника).',
    size=11
)

doc.add_heading('6.5 Расчёт зарплаты  /api/v1/payroll-periods/', level=2)
add_table(
    ['Метод', 'Эндпоинт', 'Описание'],
    [
        ['GET', '/api/v1/payroll-periods/', 'Список всех периодов зарплаты'],
        ['POST', '/api/v1/payroll-periods/create/', 'Создание нового периода'],
        ['POST', '/api/v1/payroll-periods/<id>/recalculate/', 'Запуск async пересчёта зарплаты'],
        ['GET', '/api/v1/payroll-periods/<id>/employees/', 'Зарплаты сотрудников за период'],
        ['GET', '/api/v1/payroll-periods/employee-payrolls/<id>/', 'Зарплата конкретного сотрудника'],
        ['POST', '/api/v1/payroll-periods/employee-payrolls/<id>/finalize/', 'Финализация одной зарплаты'],
        ['POST', '/api/v1/payroll-periods/employee-payrolls/finalize/', 'Массовая финализация'],
    ]
)

doc.add_heading('6.6 Дашборд  /api/v1/dashboard/', level=2)
add_paragraph('GET /api/v1/dashboard/ — сводная информация о предприятии на текущий день.', bold=True)
add_code_block([
    '{',
    '  "summary": {',
    '    "total_employees": 120,',
    '    "total_departments": 8,',
    '    "today_present": 98,',
    '    "today_present_percent": 81.67,',
    '    "today_present_change_percent": 3.2,',
    '    "today_late": 12,',
    '    "today_late_percent": 12.24,',
    '    "today_late_change_percent": -5.1',
    '  },',
    '  "series": {',
    '    "activity_7_days": [',
    '      {"date": "2026-03-26", "present_count": 95, "total_work_seconds": 3420000, "total_late_seconds": 18000}',
    '    ]',
    '  },',
    '  "alerts": [',
    '    {"level": "warning", "code": "LATE_SPIKE", "message": "Опоздания выросли более чем на 30%"}',
    '  ],',
    '  "meta": {"as_of": "2026-04-01", "timezone": "UTC"}',
    '}',
])

# =============================================
# 7. CELERY
# =============================================
doc.add_heading('7. Асинхронные задачи Celery', level=1)

add_paragraph(
    'Celery используется для асинхронной обработки ресурсоёмких операций: '
    'обработка событий доступа и пересчёт зарплаты. Брокер — Redis, сериализация — JSON.',
    size=12
)
doc.add_paragraph()

add_table(
    ['Задача', 'Модуль', 'Повторы', 'Запуск'],
    [
        ['processing_work_session', 'apps.access_control.tasks', '3 (задержка 5 сек)', 'Django-сигнал post_save'],
        ['recalculate_payroll_period_task', 'apps.payroll.tasks', '3 (задержка 5 сек)', 'API эндпоинт recalculate'],
        ['recalculate_employee_payroll_task', 'apps.payroll.tasks', '3 (задержка 5 сек)', 'recalculate_payroll_period_task'],
    ]
)

add_paragraph(
    'Задача processing_work_session использует select_for_update() для защиты от race conditions '
    'при одновременной обработке нескольких событий одного сотрудника.',
    size=12
)

# =============================================
# 8. DEPLOYMENT
# =============================================
doc.add_heading('8. Развёртывание и настройка', level=1)

doc.add_heading('8.1 Переменные окружения', level=2)
add_table(
    ['Переменная', 'Описание', 'Пример'],
    [
        ['SECRET_KEY', 'Django секретный ключ', 'django-insecure-abc...'],
        ['DEBUG', 'Режим отладки', 'True / False'],
        ['DB_TYPE', 'Тип СУБД', 'postgres / sqlite'],
        ['DB_HOST', 'Хост базы данных', 'localhost'],
        ['DB_PORT', 'Порт СУБД', '5432'],
        ['DB_NAME', 'Имя базы данных', 'access_control_db'],
        ['DB_USER', 'Пользователь БД', 'postgres'],
        ['DB_PASSWORD', 'Пароль БД', 'secret'],
        ['CELERY_BROKER_URL', 'URL брокера Redis', 'redis://localhost:6379/0'],
        ['REDIS_HOST', 'Хост Redis', 'localhost'],
        ['REDIS_PORT', 'Порт Redis', '6379'],
    ]
)

doc.add_heading('8.2 Установка и запуск (разработка)', level=2)
add_code_block([
    '# 1. Клонирование и настройка',
    'git clone <repo-url> && cd access-control-system',
    'python3 -m venv venv && source venv/bin/activate',
    'pip install -r requirements/base.txt',
    '',
    '# 2. База данных',
    'python manage.py migrate',
    'python manage.py createsuperuser',
    '',
    '# 3. Запуск Django',
    'python manage.py runserver',
    '',
    '# 4. Celery воркер (отдельный терминал)',
    'celery -A src.celery_app worker --loglevel=info',
    '',
    '# 5. Celery beat (отдельный терминал)',
    'celery -A src.celery_app beat --loglevel=info',
])

doc.add_heading('8.3 Первоначальное заполнение данными', level=2)
add_code_block([
    '# Создать предприятие с 3 отделами и 2 подотделами',
    'python manage.py create_ent --dep 3 --part 2',
    '',
    '# Создать 10 сотрудников для предприятия ID=1',
    'python manage.py create_employees --id 1 --count 10',
    '',
    '# Сгенерировать тестовые события доступа за март 2026',
    'python manage.py create_access_control --id 1',
])

# =============================================
# 9. WORKFLOWS
# =============================================
doc.add_heading('9. Рабочие процессы системы', level=1)

doc.add_heading('9.1 Учёт рабочего времени', level=2)
add_code_block([
    'Турникет / устройство доступа',
    '        ↓',
    'POST /api/v1/access-controls/create/   ←  ENTER или LEAVE событие',
    '        ↓',
    'AccessEvent сохранён в БД',
    '        ↓  Django Signal post_save',
    'processing_work_session.delay(event_id)  →  Redis Queue',
    '        ↓  Celery Worker',
    'ENTER: закрыть старую сессию → открыть новую WorkSession',
    'LEAVE: закрыть текущую WorkSession (ended, duration_seconds)',
    '        ↓',
    '_update_daily_attendance()  →  обновить DailyAttendance',
])

doc.add_heading('9.2 Расчёт заработной платы', level=2)
add_code_block([
    'POST /api/v1/payroll-periods/create/           ← создать период',
    '        ↓',
    'POST /api/v1/payroll-periods/<id>/recalculate/ ← запустить расчёт',
    '        ↓',
    'recalculate_payroll_period_task → Redis Queue',
    '        ↓  для каждого сотрудника',
    'recalculate_employee_payroll_task',
    '        ↓',
    'calculate_employee_payroll():',
    '  ├── Получить DailyAttendance за период',
    '  ├── Рассчитать BASE / OVERTIME / PENALTY',
    '  └── Сохранить EmployeePayroll + PayrollItems',
    '        ↓',
    'POST /employee-payrolls/<id>/finalize/         ← подтвердить зарплату',
])

doc.add_heading('9.3 Обновление компенсации сотрудника', level=2)
add_code_block([
    'PATCH /api/v1/employees/employees/<id>/update/',
    '        ↓  atomic transaction',
    'update_employee_compensation():',
    '  ├── Деактивировать старый EmployeeDetail (is_active=False)',
    '  ├── Создать новый EmployeeDetail (is_active=True)',
    '  └── Создать EmployeeWorkDay записи для нового графика',
])

# =============================================
# FOOTER
# =============================================
doc.add_paragraph()
doc.add_paragraph()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('Access Control System v1.0.1  ·  Документация подготовлена 2026-04-01  ·  ChoriyevJamshid')
run.font.name = 'Times New Roman'
run.font.size = Pt(10)
run.font.color.rgb = RGBColor(0x88, 0x88, 0x88)

# Save
output_path = '/home/jamshid/Projects/Python/access-control-system/docs/DOCUMENTATION.docx'
doc.save(output_path)
print(f'Saved: {output_path}')
