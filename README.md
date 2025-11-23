# uralcode

## Ожидаемая стуктура
```
.
├── docker-compose.yml          # Оркестрация всех контейнеров
├── Makefile                    # Быстрые команды: make up, make seed, make logs
├── README.md                   # Описание проекта для жюри
│
├── backend/                    # API на Python (FastAPI)
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # Точка входа (FastAPI app)
│   │   ├── config.py           # Переменные окружения (DB_URL)
│   │   ├── database.py         # Сессия SQLAlchemy
│   │   ├── models.py           # ТА САМАЯ схема БД (CourseVariant и т.д.)
│   │   ├── schemas.py          # Pydantic модели (Request/Response)
│   │   │
│   │   ├── api/                # Роутеры (Эндпоинты)
│   │   │   ├── __init__.py
│   │   │   ├── students.py     # GET /me, GET /skills
│   │   │   ├── courses.py      # GET /roadmap (логика графа)
│   │   │   └── analytics.py    # POST /webhook/engagement (от внешней системы)
│   │   │
│   │   └── services/           # Бизнес-логика
│   │       ├── recommender.py  # Алгоритм подбора курсов (Dijkstra или жадный)
│   │       └── trajectory.py   # Логика "Что, если?"
│   │
│   └── scripts/                # Скрипты для заполнения БД
│       └── seed_fake_data.py   # ГЕНЕРАТОР ФЕЙКОВЫХ ДАННЫХ (Критично важно!)
│
├── frontend/                   # UI (React / Next.js / Vue)
│   ├── Dockerfile
│   ├── package.json
│   ├── src/
│   │   ├── components/
│   │   │   ├── SkillRadar.tsx  # Паутинка навыков (Chart.js / Recharts)
│   │   │   ├── Roadmap.tsx     # Визуализация графа (React Flow)
│   │   │   └── CourseCard.tsx  # Карточка с переключателем сложности
│   │   ├── pages/
│   │   │   ├── index.tsx       # Дашборд
│   │   │   └── builder.tsx     # Страница "Что, если?"
│   │   └── api/                # Клиент к бэкенду (axios)
│   └── public/                 # Картинки, лого УрФУ
│
├── ml/                         # Data Science сервис
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                 # Микросервис (FastAPI) с ендпоинтом /predict
│   ├── model/
│   │   ├── training.ipynb      # Ноутбук, где вы обучали IsolationForest
│   │   └── anomaly_model.pkl   # Сохраненная модель
│   └── data_generator.py       # Генерация CSV для обучения модели
│
├── db/                         # Управление базой данных
│   ├── Dockerfile              # PostgreSQL image
│   ├── init.sql                # Скрипт инициализации (если не используем Alembic)
│   └── alembic/                # Миграции (рекомендую настроить)
│       └── versions/
│
└── devops/                     # Конфиги для деплоя
    └── nginx/
        └── default.conf        # Проксирование запросов (api -> backend, / -> front)
```