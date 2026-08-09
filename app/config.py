from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    BASE_URL: str = "http://localhost:8000"
    DATABASE_URL: str = "sqlite:///./shorturl.db"
    SHORT_CODE_LENGTH: int = 6
    SECRET_KEY: str = "change-me"
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"
    SESSION_MAX_AGE: int = 86400
    
    APP_NAME: str = "EpuUrl"
    APP_FOOTER: str = "© 2024 EpuUrl. Nhanh, Đẹp, Bảo mật."

    class Config:
        env_file = ".env"

settings = Settings()
