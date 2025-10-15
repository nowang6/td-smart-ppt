from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # 定义配置字段
    LLM_BASE_URL: str = ""
    LLM_API_KEY: str = ""
    LLM_MODEL: str = ""
    LANGFUSE_PUBLIC_KEY: str = ""
    LANGFUSE_SECRET_KEY: str = ""
    PEXELS_API_KEY: str = ""
    BOCHA_API_KEY: str = ""
    DASHSCOPE_API_KEY: str = ""
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# 创建全局 settings 实例
settings = Settings()

