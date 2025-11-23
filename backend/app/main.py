import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.config import settings
from app.utils.exceptions import (
    EducationPlannerException,
    education_planner_exception_handler,
    general_exception_handler,
    sqlalchemy_exception_handler,
    validation_exception_handler,
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = FastAPI(
    title="Education Planner API",
    description="""
    ## Динамический планировщик образовательной траектории
    
    API для студентов УрФУ, помогающее:
    - 📚 Выбирать специальность и курсы
    - 📊 Отслеживать развитие навыков
    - 🎯 Получать персональные рекомендации
    - 🔄 Моделировать смену специальности
    
    ### Основные возможности:
    
    - **Аутентификация**: JWT токены (access + refresh)
    - **Специальности**: Просмотр roadmap и матрицы навыков
    - **Курсы**: Запись, прохождение, отслеживание прогресса
    - **Навыки**: Древовидная структура, gap-анализ
    - **Рекомендации**: Умные подсказки по выбору курсов
    - **What-If анализ**: Моделирование смены специальности
    
    ### Для начала работы:
    1. Зарегистрируйтесь через `/api/auth/register`
    2. Получите токен через `/api/auth/login`
    3. Используйте токен в заголовке: `Authorization: Bearer <token>`
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={"name": "Education Planner Team", "email": "support@edu-planner.ru"},
    license_info={
        "name": "MIT",
    },
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Регистрация обработчиков исключений
app.add_exception_handler(
    EducationPlannerException, education_planner_exception_handler
)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


@app.get("/")
async def root():
    """Корневой эндпоинт для проверки работы API"""
    return {"message": "Education Planner API", "version": "1.0.0", "docs": "/docs"}


@app.get("/health")
async def health_check():
    """Проверка здоровья приложения"""
    return {"status": "healthy"}


# Подключение роутеров
from app.api import (
    auth,
    courses,
    minors,
    orbit,
    recommendations,
    resume,
    skills,
    specializations,
    students,
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(
    specializations.router, prefix="/api/specializations", tags=["specializations"]
)
app.include_router(courses.router, prefix="/api/courses", tags=["courses"])
app.include_router(skills.router, prefix="/api/skills", tags=["skills"])
app.include_router(students.router, prefix="/api/students", tags=["students"])
app.include_router(
    recommendations.router, prefix="/api/recommendations", tags=["recommendations"]
)
app.include_router(minors.router, prefix="/api/minors", tags=["minors"])
app.include_router(orbit.router, prefix="/api/orbit", tags=["orbit"])
app.include_router(resume.router, prefix="/api/resume", tags=["resume"])
