"""
Configuration management for Cupid Yukio Soul Match Bot.

This module centralizes all configuration settings including:
- Environment variables
- Database settings
- API keys and tokens
- Bot settings
- URLs and endpoints
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class DatabaseConfig:
    """Database configuration settings."""
    
    # MongoDB Configuration
    # MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")  # 默认本地连接，已注释，保留做参考
    # MONGO_USERNAME = os.getenv("MONGO_USERNAME")
    # MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
    # MONGO_DATABASE = os.getenv("MONGO_DATABASE", "lovelush_db")
    
    # ====== 远程 MongoDB 配置（已根据用户要求修改） ======
    # 账号：root，密码：Awr20020311，主机：8.216.32.239，端口：27017，数据库：lovelush_db
    MONGO_URI = "mongodb://8.216.32.239:27017/"
    MONGO_USERNAME = "root"
    MONGO_PASSWORD = "Awr20020311"
    MONGO_DATABASE = "lovelush_db"
    # =========================================
    
    # Collections
    SESSIONS_COLLECTION = "telegram_sessions"
    USER_COLLECTION = "User"  # 修改：用户表集合名称为User
    
    @classmethod
    def get_auth_uri(cls) -> str:
        """Get MongoDB URI with authentication if credentials are provided."""
        if cls.MONGO_USERNAME and cls.MONGO_PASSWORD:
            if "mongodb://" in cls.MONGO_URI:
                return cls.MONGO_URI.replace("mongodb://", f"mongodb://{cls.MONGO_USERNAME}:{cls.MONGO_PASSWORD}@")
            elif "mongodb+srv://" in cls.MONGO_URI:
                return cls.MONGO_URI.replace("mongodb+srv://", f"mongodb+srv://{cls.MONGO_USERNAME}:{cls.MONGO_PASSWORD}@")
        return cls.MONGO_URI


class APIConfig:
    """API configuration settings."""
    
    # Gemini AI Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL_NAME = "gemini-2.5-pro"
    
    # Backend API Configuration
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")  # 本地服务器API地址
    
    # Telegram Bot Configuration
    # yukio原来的 token（已注释）
    # TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8029098791:AAE2pWPLPEsiIBPTu9-OOQC3zF2a9QbaW8s")
    # lushia新的 token（已注释）
    # TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8014721220:AAHUJui6sV82nX80uG14ynlF8TeQ3xpSF0U")
    # lyra新的 token（当前使用）
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7937420230:AAHY6hFQ0N7ypjG7-26svO09byXgyNo3vhQ")  # lyra新token
    TELEGRAM_BOT_TOKEN_TEST = os.getenv("TELEGRAM_BOT_TOKEN_TEST", "7960283253:AAEeMcp1XGJjIe8iwpVwd3W2gKvlTfRPJUw")
    
    @classmethod
    def validate_gemini_key(cls) -> bool:
        """Validate that Gemini API key is set."""
        return bool(cls.GEMINI_API_KEY)


class BotConfig:
    """Bot behavior and UI configuration."""
    
    # Bot URLs
    BOT_WEBAPP_URL = "https://t.me/CupidYukioBot/app?startapp"
    BOT_WEBAPP_URL_TEST = "https://t.me/CupidYukioTestbot/app?startapp"
    
    # Gender selection options
    GENDER_OPTIONS = {
        "male": "I am a boy!",  # 原文：我是男孩子！
        "female": "I am a girl!"  # 原文：我是女孩子！
    }
    
    # Target gender selection options
    TARGET_GENDER_OPTIONS = {
        "women": "Women",  # 原文：女性
        "men": "Men",      # 原文：男性
        "no_matter": "No matter"  # 原文：无所谓
    }
    
    # Messages
    GREETING_MESSAGE = "Let's get started! First, please tell me if you are a boy or a girl? 🥰"  # 原文：好的，让我们开始吧！首先，请告诉我你是男孩子还是女孩子？ 🥰
    AGE_QUESTION_MESSAGE = "Hey mister! Before we start, let me know how old are you?"  # 原文：好的先生，你多大了呢？
    AGE_QUESTION_MESSAGE_FEMALE = "Hey miss! Before we start, let me know how old are you?"  # 原文：好的小姐，你多大了呢？
    TARGET_GENDER_QUESTION_MESSAGE = "Who are you looking for?"  # 原文：你在寻找谁？
    WELCOME_MESSAGE = "Welcome to our soul matching game! Click the button below to start your experience!"  # 原文：欢迎来到我们的灵魂匹配游戏！点击下方按钮开始体验吧！
    READY_MESSAGE = "We're about to start the game, are you ready?"  # 原文：接下来我们就要开始游戏了哟，准备好了吗？
    VIEW_MALE_ANSWERS_MESSAGE = "Click the button below to see how the boys answered these questions."  # 原文：点击下方按钮查看男生是如何回答这些问题的
    ERROR_CONFIG_MESSAGE = "❌ Bot configuration error. Please contact support."
    ERROR_SESSION_MESSAGE = "❌ Sorry, there was an error setting up your session. Please try /start again."
    ERROR_PROCESSING_MESSAGE = "❌ Sorry, there was an error processing your message. Please try again or use /start to restart."
    START_PROMPT_MESSAGE = "Please start by selecting your gender using /start command! 🥰"
    INVALID_AGE_MESSAGE = "Please enter a valid age (number between 13 and 100)."  # 原文：请输入有效年龄（13-100之间的数字）
    
    # Button texts
    START_EXPERIENCE_BUTTON = "Start Experience"  # 原文：开始体验
    VIEW_MALE_ANSWERS_BUTTON = "View Boys' Answers"  # 原文：查看男生回答
    
    # Typing indicator
    TYPING_DURATION = 4  # seconds
    
    # Session management
    END_TAG = "#end"


class LoggingConfig:
    """Logging configuration settings."""
    
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_LEVEL = 'INFO'


class PromptConfig:
    """Prompt file configuration."""
    
    PROMPT_DIR = "prompt"
    PROMPT_FILES = {
        "role": "role.md",
        "object": "object.md", 
        "skill": "skill.md",
        "constraint": "constraint.md",
        "workflow": "workflow.md",
        "male": "male.md",
        "female": "female.md",
        "neutral": "neutral.md"
    }


class Config:
    """Main configuration class that aggregates all config sections."""
    
    # Import all config sections
    Database = DatabaseConfig
    API = APIConfig
    Bot = BotConfig
    Logging = LoggingConfig
    Prompt = PromptConfig
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that all required configuration is present."""
        if not cls.API.validate_gemini_key():
            print("❌ GEMINI_API_KEY is not set in environment variables")
            return False
        return True
    
    @classmethod
    def get_webapp_url(cls, use_test: bool = False) -> str:
        """Get the appropriate webapp URL based on environment."""
        return cls.Bot.BOT_WEBAPP_URL_TEST if use_test else cls.Bot.BOT_WEBAPP_URL
    
    @classmethod
    def get_bot_token(cls, use_test: bool = False) -> str:
        """Get the appropriate bot token based on environment."""
        return cls.API.TELEGRAM_BOT_TOKEN_TEST if use_test else cls.API.TELEGRAM_BOT_TOKEN


# Convenience functions for backward compatibility
def get_mongo_uri() -> str:
    """Get MongoDB URI with authentication."""
    return DatabaseConfig.get_auth_uri()


def get_mongo_database() -> str:
    """Get MongoDB database name."""
    return DatabaseConfig.MONGO_DATABASE


def get_gemini_api_key() -> Optional[str]:
    """Get Gemini API key."""
    return APIConfig.GEMINI_API_KEY


def get_telegram_bot_token(use_test: bool = False) -> str:
    """Get Telegram bot token."""
    return Config.get_bot_token(use_test) 