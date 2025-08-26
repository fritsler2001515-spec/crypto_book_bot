import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Telegram Bot
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "your_telegram_bot_token_here")
    
    # Database (PostgreSQL) - поддержка DATABASE_URL для production
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # Database fallback настройки для development
    DB_HOST: str = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "postgres")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASS: str = os.getenv("DB_PASS", "user123")
    
    # Дополнительные настройки из .env
    CHAT_IDS: str = os.getenv("CHAT_IDS", "")
    
    # Web App URL
    WEBAPP_URL: str = os.getenv("WEBAPP_URL", "https://your-ngrok-url.ngrok-free.app")
    
    @property
    def DB_URL(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL.replace("postgresql://", "postgresql://", 1)
        return f"postgresql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def ASYNC_DB_URL(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8001"))
    
    # External APIs
    COINGECKO_API_URL: str = "https://api.coingecko.com/api/v3"
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Игнорируем дополнительные поля


settings = Settings() 