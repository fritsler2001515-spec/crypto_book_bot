#!/usr/bin/env python3
"""
Тест роутера
"""

from fastapi import APIRouter, FastAPI

# Создаем роутер
api_router = APIRouter(prefix="/api")

@api_router.get("/test")
async def test_endpoint():
    return {"message": "test"}

# Создаем приложение
app = FastAPI()
app.include_router(api_router)

# Проверяем роуты
print("Доступные роуты:")
for route in app.routes:
    print(f"  {route.path}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
