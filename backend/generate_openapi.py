"""
Скрипт для генерации OpenAPI-схемы в файл
"""

import json

from app.main import app

if __name__ == "__main__":
    # Получаем OpenAPI-схему
    openapi_schema = app.openapi()

    # Сохраняем в файл с красивым форматированием
    with open("openapi.json", "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, ensure_ascii=False, indent=2)

    print("✅ OpenAPI-схема успешно сохранена в openapi.json")
    print(f"   Версия API: {openapi_schema['info']['version']}")
    print(f"   Endpoints: {len(openapi_schema['paths'])}")
