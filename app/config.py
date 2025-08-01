from pathlib import Path
import os
from dotenv import load_dotenv
from typing import Optional

PROJECT_DIR = Path(__file__).resolve().parents[1]

load_dotenv()


class Settings:
    # 项目基本信息
    PROJECT_NAME: str = "NewLoveLushUserService"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # MongoDB配置
    # MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    # MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "miracle_demo")
    # MONGODB_USERNAME: str = os.getenv("MONGODB_USERNAME", "root")
    # MONGODB_PASSWORD: str = os.getenv("MONGODB_PASSWORD", "Awr20020311")
    # MONGODB_AUTH_SOURCE: str = os.getenv("MONGODB_AUTH_SOURCE", "admin")

    # 本地测试数据库
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "local_test_db"
    MONGODB_USERNAME: str = ""
    MONGODB_PASSWORD: str = ""
    MONGODB_AUTH_SOURCE: str = ""

    # JWT配置 (为了保持结构完整性，即使当前未使用)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # 默认30分钟

    # AI API配置
    # 豆包API配置（保留，但暂时不使用）
    DOUBAO_API_KEY: str = os.getenv("DOUBAO_API_KEY", "1e65c3d6-b827-4706-9fa8-93732bed0a8a")
    DOUBAO_API_URL: str = os.getenv("DOUBAO_API_URL", "https://api.doubao.com/v1/chat/completions")
    DOUBAO_MODEL_NAME: str = os.getenv("DOUBAO_MODEL_NAME", "doubao-seed-1.6-250615")
    
    # Gemini API配置
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_API_URL: str = os.getenv("GEMINI_API_URL", "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent")
    GEMINI_MODEL_NAME: str = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
    
    # Moonshot API配置（当前使用）
    KIMI_API_KEY: str = os.getenv("KIMI_API_KEY", "sk-k6FqWbmEJJa9TKxK39fjCEflSG7JraFGlK2BnhAYcaHi89PJ")
    KIMI_API_URL: str = os.getenv("KIMI_API_URL", "https://api.moonshot.cn/v1/chat/completions")
    KIMI_MODEL_NAME: str = os.getenv("KIMI_MODEL_NAME", "moonshot-v1-8k")
    
    # 当前使用的AI服务（可以切换）
    CURRENT_AI_SERVICE: str = os.getenv("CURRENT_AI_SERVICE", "kimi")  # "kimi", "gemini" 或 "doubao"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 