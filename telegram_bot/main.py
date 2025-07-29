import logging
import os
import asyncio
import httpx  # 新增：用于HTTP请求
from datetime import datetime, UTC
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from matchmaker_bot_requests import MatchmakerBot
from config import Config
import re  # 新增：导入正则模块

# 导入schema定义
from schema.UserManagement import (
    CreateNewUserRequest, CreateNewUserResponse,
    EditUserAgeRequest, EditUserAgeResponse,
    EditTargetGenderRequest, EditTargetGenderResponse,
    EditSummaryRequest, EditSummaryResponse,
    GetUserInfoWithUserIdRequest, GetUserInfoWithUserIdResponse,
    DeactivateUserRequest, DeactivateUserResponse
)

# MongoDB setup with authentication
from pymongo import MongoClient
client = MongoClient(Config.Database.get_auth_uri())
db = client[Config.Database.MONGO_DATABASE]
sessions_collection = db[Config.Database.SESSIONS_COLLECTION]
users_collection = db[Config.Database.USER_COLLECTION]  # 新增：用户表集合

# API配置
API_BASE_URL = Config.API.API_BASE_URL  # 从配置文件获取API地址

logging.basicConfig(
    format=Config.Logging.LOG_FORMAT,
    level=getattr(logging, Config.Logging.LOG_LEVEL)
)

# Store user bot instances
user_bots = {}
# Store user session stage (e.g., waiting_ready, in_interview)
user_stage = {}  # 记录每个用户的会话阶段
# Store user gender detection status
user_gender_detected = {}  # 记录用户是否已经完成性别识别
# Store user age
user_age = {}  # 记录用户年龄
# Store user target gender
user_target_gender = {}  # 记录用户目标性别

# ========== API调用函数 ==========


async def create_new_user_api(telegram_user_id: int, telegram_user_name: str, gender: int):
    """调用后端API创建新用户，使用schema定义"""
    try:
        async with httpx.AsyncClient() as client:
            url = f"{API_BASE_URL}/api/v1/UserManagement/create_new_user"
            
            # 使用schema构造请求
            request = CreateNewUserRequest(
                telegram_user_id=telegram_user_id,
                telegram_user_name=telegram_user_name,
                gender=gender
            )
            req_body = request.dict()
            
            logging.info(f"[create_new_user_api] 请求URL: {url}")
            logging.info(f"[create_new_user_api] 请求体: {req_body}")
            
            response = await client.post(url, json=req_body, timeout=10.0)
            logging.info(f"[create_new_user_api] 响应状态: {response.status_code}")
            logging.info(f"[create_new_user_api] 响应内容: {response.text}")
            
            if response.status_code == 200:
                # 使用schema解析响应
                response_data = CreateNewUserResponse(**response.json())
                logging.info(f"User created via API for telegram_user_id {telegram_user_id}: success={response_data.success}, user_id={response_data.user_id}")
                return response_data.user_id if response_data.success else None
            else:
                logging.error(f"API call failed for create_new_user: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        logging.error(f"Error calling create_new_user API for telegram_user_id {telegram_user_id}: {str(e)}")
        return None

async def edit_user_age_api(user_id: int, age: int):
    """调用后端API编辑用户年龄，使用schema定义"""
    try:
        async with httpx.AsyncClient() as client:
            url = f"{API_BASE_URL}/api/v1/UserManagement/edit_user_age"
            
            # 使用schema构造请求
            request = EditUserAgeRequest(user_id=user_id, age=age)
            req_body = request.dict()
            
            logging.info(f"[edit_user_age_api] 请求URL: {url}")
            logging.info(f"[edit_user_age_api] 请求体: {req_body}")
            
            response = await client.post(url, json=req_body, timeout=10.0)
            logging.info(f"[edit_user_age_api] 响应状态: {response.status_code}")
            logging.info(f"[edit_user_age_api] 响应内容: {response.text}")
            
            if response.status_code == 200:
                # 使用schema解析响应
                response_data = EditUserAgeResponse(**response.json())
                logging.info(f"User age updated via API for user_id {user_id}: success={response_data.success}")
                return response_data.success
            else:
                logging.error(f"API call failed for edit_user_age: {response.status_code} - {response.text}")
                return False
    except Exception as e:
        logging.error(f"Error calling edit_user_age API for user_id {user_id}: {str(e)}")
        return False

async def edit_target_gender_api(user_id: int, target_gender: int):
    """调用后端API编辑用户目标性别，使用schema定义"""
    try:
        async with httpx.AsyncClient() as client:
            url = f"{API_BASE_URL}/api/v1/UserManagement/edit_target_gender"
            
            # 使用schema构造请求
            request = EditTargetGenderRequest(user_id=user_id, target_gender=target_gender)
            req_body = request.dict()
            
            logging.info(f"[edit_target_gender_api] 请求URL: {url}")
            logging.info(f"[edit_target_gender_api] 请求体: {req_body}")
            
            response = await client.post(url, json=req_body, timeout=10.0)
            logging.info(f"[edit_target_gender_api] 响应状态: {response.status_code}")
            logging.info(f"[edit_target_gender_api] 响应内容: {response.text}")
            
            if response.status_code == 200:
                # 使用schema解析响应
                response_data = EditTargetGenderResponse(**response.json())
                logging.info(f"User target gender updated via API for user_id {user_id}: success={response_data.success}")
                return response_data.success
            else:
                logging.error(f"API call failed for edit_target_gender: {response.status_code} - {response.text}")
                return False
    except Exception as e:
        logging.error(f"Error calling edit_target_gender API for user_id {user_id}: {str(e)}")
        return False

async def edit_summary_api(user_id: int, summary: str):
    """调用后端API编辑用户总结，使用schema定义"""
    try:
        async with httpx.AsyncClient() as client:
            url = f"{API_BASE_URL}/api/v1/UserManagement/edit_summary"
            
            # 使用schema构造请求
            request = EditSummaryRequest(user_id=user_id, summary=summary)
            req_body = request.dict()
            
            logging.info(f"[edit_summary_api] 请求URL: {url}")
            logging.info(f"[edit_summary_api] 请求体: {req_body}")
            
            response = await client.post(url, json=req_body, timeout=10.0)
            logging.info(f"[edit_summary_api] 响应状态: {response.status_code}")
            logging.info(f"[edit_summary_api] 响应内容: {response.text}")
            
            if response.status_code == 200:
                # 使用schema解析响应
                response_data = EditSummaryResponse(**response.json())
                logging.info(f"User summary updated via API for user_id {user_id}: success={response_data.success}")
                return response_data.success
            else:
                logging.error(f"API call failed for edit_summary: {response.status_code} - {response.text}")
                return False
    except Exception as e:
        logging.error(f"Error calling edit_summary API for user_id {user_id}: {str(e)}")
        return False

# ========== 用户ID映射存储 ==========
# 由于后端API使用user_id（内部ID）而前端使用telegram_user_id，需要维护映射
telegram_to_user_id_map = {}  # telegram_user_id -> user_id 映射

# Test MongoDB connection


def test_mongodb_connection():
    """Test MongoDB connection and authentication."""
    try:
        # Test the connection by listing collections
        collections = db.list_collection_names()
        logging.info(
    f"MongoDB connection successful. Available collections: {collections}")
        return True
    except Exception as e:
        logging.error(f"MongoDB connection failed: {str(e)}")
        return False

# MongoDB helper functions


def save_session_to_mongodb(user_id: int, gender: str):
    """Save initial session data to MongoDB using user_id as the document ID."""
    try:
        session_data = {
            '_id': user_id,
            'gender': gender,
            'final_string': None,
            'started_at': datetime.now(UTC),
            'created_at': datetime.now(UTC)
        }
        sessions_collection.replace_one(
            {'_id': user_id}, session_data, upsert=True)
        logging.info(f"Session saved to MongoDB for user {user_id}")
        return True
    except Exception as e:
        logging.error(
    f"Error saving session to MongoDB for user {user_id}: {
        str(e)}")
        return False


def get_session_from_mongodb(user_id: int):
    """Get session data from MongoDB using user_id."""
    try:
        return sessions_collection.find_one({'_id': user_id})
    except Exception as e:
        logging.error(
    f"Error getting session from MongoDB for user {user_id}: {
        str(e)}")
        return None


def save_gemini_response_to_mongodb(user_id: int, final_string: str):
    """Save final string to MongoDB when #end tag is detected."""
    try:
        sessions_collection.update_one(
            {'_id': user_id},
            {
                '$set': {
                    'final_string': final_string
                }
            }
        )
        logging.info(f"Final string saved to MongoDB for user {user_id}")
        return True
    except Exception as e:
        logging.error(
    f"Error saving final string to MongoDB for user {user_id}: {
        str(e)}")
        return False

# ========== 新增：保存完整会话信息到MongoDB ==========


def save_final_session_to_mongodb(
    user_id: int,
    gender: str,
    turns: int,
    started_at,
    ended_at,
    final_string: str,
    filter_questions: str,
     user_rating: float):
    """保存完整会话信息到MongoDB，包括用户id、性别、轮数、时间、总结、筛选问题、评分。user_rating支持小数。"""
    try:
        sessions_collection.update_one(
            {'_id': user_id},
            {
                '$set': {
                    'gender': gender,
                    'turns': turns,
                    'started_at': started_at,
                    'ended_at': ended_at,
                    'final_string': final_string,
                    'filter_questions': filter_questions,
                    'user_rating': user_rating
                },
                '$inc': {'experience_count': 1}  # 新增：体验次数+1
            },
            upsert=True
        )
        logging.info(f"Final session info saved to MongoDB for user {user_id}")
        return True
    except Exception as e:
        logging.error(
    f"Error saving final session info to MongoDB for user {user_id}: {
        str(e)}")
        return False


# ========== 新增：轮数统计 ==========
user_turns = {}  # 记录每个用户的对话轮数
user_started_at = {}  # 记录每个用户的会话开始时间
user_final_string = {}  # 记录每个用户的完整总结
user_filter_questions = {}  # 记录每个用户的筛选问题
user_waiting_rating = {}  # 记录是否等待评分

# ========== 移除白名单变量和所有相关判断 ==========
# INTERNAL_USER_IDS = [7773152103, 8062279607]  # 允许这两个Telegram号反复体验
# ========== 新增：已体验用户记录（用于白名单机制） ==========
experienced_users = set()  # 记录已经完成体验的非白名单用户

# ========== 新增：用户数据管理函数 ==========


async def create_or_update_user(telegram_user_id: int, telegram_user_name: str = None, gender: int = None):
    """创建或更新用户基本信息，维护telegram_user_id到user_id的映射"""
    try:
        # 检查是否已存在映射
        if telegram_user_id in telegram_to_user_id_map:
            user_id = telegram_to_user_id_map[telegram_user_id]
            # 验证后端是否真的存在
            exists = await check_user_exists_api(user_id)
            if exists:
                logging.info(f"[create_or_update_user] telegram_user_id {telegram_user_id} 已映射到 user_id {user_id}，后端存在")
                return True
            else:
                # 映射失效，清理并重新创建
                telegram_to_user_id_map.pop(telegram_user_id, None)
                logging.warning(f"[create_or_update_user] 映射失效，清理 telegram_user_id {telegram_user_id}")
        
        # 创建新用户
        if gender is None:
            logging.warning(f"Cannot create user without gender for telegram_user_id {telegram_user_id}")
            return False
            
        api_user_id = await create_new_user_api(telegram_user_id, telegram_user_name, gender)
        if api_user_id:
            # 建立映射
            telegram_to_user_id_map[telegram_user_id] = api_user_id
            logging.info(f"[create_or_update_user] 成功创建并映射 telegram_user_id {telegram_user_id} -> user_id {api_user_id}")
            return True
        else:
            logging.error(f"Failed to create user via API for telegram_user_id {telegram_user_id}")
            return False
    except Exception as e:
        logging.error(f"Error creating/updating user via API for telegram_user_id {telegram_user_id}: {str(e)}")
        return False

# ========== 注释掉的MongoDB版本 ==========
# def create_or_update_user(user_id: int, telegram_user_name: str = None):
#     """创建或更新用户基本信息，使用user_id作为主键"""
#     try:
#         existing = users_collection.find_one({'_id': user_id})
#         if existing:
#             # 只更新用户名和更新时间，不重置其他字段
#             users_collection.update_one(
#                 {'_id': user_id},
#                 {'$set': {'telegram_user_name': telegram_user_name, 'updated_at': datetime.now(UTC)}}
#             )
#         else:
#             user_data = {
#                 '_id': user_id,
#                 'telegram_user_name': telegram_user_name,
#                 'gender': None,  # 1=女性, 2=男性, 3=其他
#                 'age': None,
#                 'target_gender': None,  # 1=女性, 2=男性, 3=其他
#                 'user_personality_summary': None,  # 只存储最后的总结
#                 'ai_response': None,  # 新增：存储AI的实时响应
#                 'user_rating': None,
#                 'match_ids': [],
#                 'blocked_user_ids': [],
#                 'created_at': datetime.now(UTC),
#                 'updated_at': datetime.now(UTC)
#             }
#             users_collection.insert_one(user_data)
#         logging.info(f"User created/updated in MongoDB for user {user_id}")
#         return True
#     except Exception as e:
#         logging.error(f"Error creating/updating user in MongoDB for user {user_id}: {str(e)}")
#         return False


async def save_user_gender(user_id: int, gender: str):
    """保存用户性别，直接使用telegram_user_id调用API"""
    try:
        # 性别在创建用户时已经设置，这里只需要确保用户已创建
        # 由于创建用户时已包含性别，此函数主要用于确认
        logging.info(f"User gender processed for telegram_user_id {user_id}: {gender}")
        return True
    except Exception as e:
        logging.error(f"Error processing user gender for telegram_user_id {user_id}: {str(e)}")
        return False

# ========== 注释掉的MongoDB版本 ==========
# def save_user_gender(user_id: int, gender: str):
#     """保存用户性别到用户表"""
#     try:
#         # 转换性别字符串为数字
#         gender_map = {
#             'female': 1,  # 女性
#             'male': 2,    # 男性
#             'neutral': 3, # 其他
#             'other': 3    # 其他
#         }
#         gender_int = gender_map.get(gender.lower(), 3)
#
#         users_collection.update_one(
#             {'_id': user_id},
#             {
#                 '$set': {
#                     'gender': gender_int,
#                     'updated_at': datetime.now(UTC)
#                 }
#             }
#         )
#         logging.info(f"User gender saved to MongoDB for user {user_id}: {gender_int}")
#         return True
#     except Exception as e:
#         logging.error(f"Error saving user gender to MongoDB for user {user_id}: {str(e)}")
#         return False


async def save_user_age(telegram_user_id: int, age: int):
    """保存用户年龄，通过映射获取user_id"""
    try:
        if telegram_user_id not in telegram_to_user_id_map:
            logging.error(f"telegram_user_id {telegram_user_id} not found in mapping, cannot save age")
            return False
            
        user_id = telegram_to_user_id_map[telegram_user_id]
        success = await edit_user_age_api(user_id, age)
        if success:
            logging.info(f"User age saved via API for telegram_user_id {telegram_user_id} (user_id {user_id}): {age}")
            return True
        else:
            logging.error(f"Failed to save user age via API for telegram_user_id {telegram_user_id}")
            return False
    except Exception as e:
        logging.error(f"Error saving user age for telegram_user_id {telegram_user_id}: {str(e)}")
        return False

# ========== 注释掉的MongoDB版本 ==========
# def save_user_age(user_id: int, age: int):
#     """保存用户年龄到用户表"""
#     try:
#         users_collection.update_one(
#             {'_id': user_id},
#             {
#                 '$set': {
#                     'age': age,
#                     'updated_at': datetime.now(UTC)
#                 }
#             }
#         )
#         logging.info(f"User age saved to MongoDB for user {user_id}: {age}")
#         return True
#     except Exception as e:
#         logging.error(f"Error saving user age to MongoDB for user {user_id}: {str(e)}")
#         return False


async def save_user_target_gender(telegram_user_id: int, target_gender: str):
    """保存用户目标性别，通过映射获取user_id"""
    try:
        target_gender_map = {
            'women': 1,     # 女性
            'men': 2,       # 男性
            'no_matter': 3  # 其他/无所谓
        }
        target_gender_int = target_gender_map.get(target_gender.lower(), 3)

        if telegram_user_id not in telegram_to_user_id_map:
            logging.error(f"telegram_user_id {telegram_user_id} not found in mapping, cannot save target gender")
            return False
            
        user_id = telegram_to_user_id_map[telegram_user_id]
        success = await edit_target_gender_api(user_id, target_gender_int)
        if success:
            logging.info(f"User target gender saved via API for telegram_user_id {telegram_user_id} (user_id {user_id}): {target_gender_int}")
            return True
        else:
            logging.error(f"Failed to save user target gender via API for telegram_user_id {telegram_user_id}")
            return False
    except Exception as e:
        logging.error(f"Error saving user target gender for telegram_user_id {telegram_user_id}: {str(e)}")
        return False

# ========== 注释掉的MongoDB版本 ==========
# def save_user_target_gender(user_id: int, target_gender: str):
#     """保存用户目标性别到用户表"""
#     try:
#         # 转换目标性别字符串为数字
#         target_gender_map = {
#             'women': 1,     # 女性
#             'men': 2,       # 男性
#             'no_matter': 3  # 其他/无所谓
#         }
#         target_gender_int = target_gender_map.get(target_gender.lower(), 3)
#
#         users_collection.update_one(
#             {'_id': user_id},
#             {
#                 '$set': {
#                     'target_gender': target_gender_int,
#                     'updated_at': datetime.now(UTC)
#                 }
#             }
#         )
#         logging.info(f"User target gender saved to MongoDB for user {user_id}: {target_gender_int}")
#         return True
#     except Exception as e:
#         logging.error(f"Error saving user target gender to MongoDB for user {user_id}: {str(e)}")
#         return False


async def save_user_personality_summary(telegram_user_id: int, summary: str):
    """保存AI生成的用户性格总结，通过映射获取user_id"""
    try:
        if telegram_user_id not in telegram_to_user_id_map:
            logging.error(f"telegram_user_id {telegram_user_id} not found in mapping, cannot save summary")
            return False
            
        user_id = telegram_to_user_id_map[telegram_user_id]
        success = await edit_summary_api(user_id, summary)
        if success:
            logging.info(f"User personality summary saved via API for telegram_user_id {telegram_user_id} (user_id {user_id})")
            return True
        else:
            logging.error(f"Failed to save user personality summary via API for telegram_user_id {telegram_user_id}")
            return False
    except Exception as e:
        logging.error(f"Error saving user personality summary for telegram_user_id {telegram_user_id}: {str(e)}")
        return False

# ========== 注释掉的MongoDB版本 ==========
# def save_user_personality_summary(user_id: int, summary: str):
#     """保存AI生成的用户性格总结到用户表"""
#     try:
#         users_collection.update_one(
#             {'_id': user_id},
#             {
#                 '$set': {
#                     'user_personality_summary': summary,
#                     'json': summary,
#                     'updated_at': datetime.now(UTC)
#                 }
#             }
#         )
#         logging.info(f"User personality summary saved to MongoDB for user {user_id}")
#         return True
#     except Exception as e:
#         logging.error(f"Error saving user personality summary to MongoDB for user {user_id}: {str(e)}")
#         return False

# ========== 注释掉的AI响应存储（API中没有对应接口） ==========
# def save_ai_response(user_id: int, response: str):
#     """保存AI的实时响应到用户表"""
#     try:
#         users_collection.update_one(
#             {'_id': user_id},
#             {
#                 '$set': {
#                     'ai_response': response,
#                     'updated_at': datetime.now(UTC)
#                 }
#             }
#         )
#         logging.info(f"AI response saved to MongoDB for user {user_id}")
#         return True
#     except Exception as e:
#         logging.error(f"Error saving AI response to MongoDB for user {user_id}: {str(e)}")
#         return False

# ========== 注释掉的用户查询（API中没有对应接口） ==========
# def get_user_from_mongodb(user_id: int):
#     """从用户表获取用户信息"""
#     try:
#         return users_collection.find_one({'_id': user_id})
#     except Exception as e:
#         logging.error(f"Error getting user from MongoDB for user {user_id}: {str(e)}")
#         return None


def detect_gender_from_text(text: str) -> str | None:
    """
    从文本中智能检测性别关键词，优先女性，再男性，使用正则整词匹配，避免 he 匹配到 her
    返回 'male', 'female' 或 None
    """
    text_lower = text.lower().strip()

    # 女性关键词集合
    female_keywords = [
        'female', 'woman', 'girl', 'lady', 'sister', 'daughter',
        'she', 'her', 'hers', 'herself'
    ]
    # 男性关键词集合
    male_keywords = [
        'male', 'man', 'boy', 'guy', 'dude', 'gentleman', 'brother', 'son',
        'he', 'him', 'his', 'himself'
    ]

    # 添加调试日志
    logging.info(f"检测性别关键词(正则) - 输入文本: '{text}' -> 小写: '{text_lower}'")

    # 优先检测女性关键词
    for keyword in female_keywords:
        # 使用正则整词匹配，忽略大小写
        if re.search(rf'\b{re.escape(keyword)}\b', text_lower):
            logging.info(f"检测到女性关键词(正则): '{keyword}'")
            return 'female'
    # 再检测男性关键词
    for keyword in male_keywords:
        if re.search(rf'\b{re.escape(keyword)}\b', text_lower):
            logging.info(f"检测到男性关键词(正则): '{keyword}'")
            return 'male'
    logging.info("未检测到性别关键词(正则)")
    return None

# 新增：异步函数，调用后端API判断用户是否已体验过


def get_api_base_url():
    from config import Config
    return Config.API.API_BASE_URL


async def check_user_exists_api(user_id: int) -> bool:
    """
    调用后端API判断用户数据是否存在，使用schema定义。
    存在返回True，不存在返回False。
    """
    api_url = get_api_base_url() + "/api/v1/UserManagement/get_user_info_with_user_id"
    try:
        async with httpx.AsyncClient() as client:
            # 使用schema构造请求
            request = GetUserInfoWithUserIdRequest(user_id=user_id)
            req_body = request.dict()
            
            logging.info(f"[check_user_exists_api] 请求URL: {api_url}")
            logging.info(f"[check_user_exists_api] 请求体: {req_body}")
            
            resp = await client.post(api_url, json=req_body, timeout=5.0)
            logging.info(f"[check_user_exists_api] 响应状态: {resp.status_code}")
            logging.info(f"[check_user_exists_api] 响应内容: {resp.text}")
            
            if resp.status_code == 200:
                # 使用schema解析响应
                response_data = GetUserInfoWithUserIdResponse(**resp.json())
                logging.info(f"User exists: user_id={response_data.user_id}, telegram_id={response_data.telegram_id}")
                return True  # 用户数据存在
            elif resp.status_code == 404:
                return False  # 用户数据不存在
            elif resp.status_code == 400 and "404: 用户不存在" in resp.text:
                return False  # 兼容后端400+404提示，用户不存在
            else:
                logging.warning(f"Unexpected status code: {resp.status_code}, response: {resp.text}")
                return True
    except Exception as e:
        logging.error(f"check_user_exists_api error: {e}")
        return True

async def get_user_by_telegram_id_api(telegram_user_id: int) -> dict | None:
    """
    根据telegram_user_id获取用户信息，返回完整用户数据或None。
    这个函数用于获取user_id进行映射。
    """
    # 注意：这里需要一个新的API端点，或者修改现有端点支持telegram_user_id查询
    # 暂时使用现有的get_user_info_with_user_id，但需要先有user_id
    # 实际上应该有一个get_user_info_with_telegram_id的端点
    logging.warning(f"get_user_by_telegram_id_api: 需要后端提供根据telegram_user_id查询的API端点")
    return None

async def check_user_exists_by_telegram_id(telegram_user_id: int) -> bool:
    """
    根据telegram_user_id检查用户是否存在，并更新映射。
    """
    try:
        # 先检查内存映射
        if telegram_user_id in telegram_to_user_id_map:
            user_id = telegram_to_user_id_map[telegram_user_id]
            # 用user_id验证后端是否存在
            exists = await check_user_exists_api(user_id)
            if exists:
                logging.info(f"[check_user_exists_by_telegram_id] telegram_user_id {telegram_user_id} 映射到 user_id {user_id}，后端存在")
                return True
            else:
                # 映射失效，清理
                telegram_to_user_id_map.pop(telegram_user_id, None)
                logging.warning(f"[check_user_exists_by_telegram_id] 映射失效，清理 telegram_user_id {telegram_user_id}")
        
        # TODO: 这里需要后端提供根据telegram_user_id查询的API
        # 目前只能返回False，表示用户不存在（需要创建）
        logging.info(f"[check_user_exists_by_telegram_id] telegram_user_id {telegram_user_id} 不在映射中，视为不存在")
        return False
    except Exception as e:
        logging.error(f"check_user_exists_by_telegram_id error: {e}")
        return False

# 新增：异步函数，调用后端API注销用户（删除用户数据）


async def deactivate_user_api(user_id: int) -> bool:
    """
    调用后端API注销用户，删除用户数据，使用schema定义。
    成功返回True，失败返回False。
    """
    api_url = get_api_base_url() + "/api/v1/UserManagement/deactivate_user"
    try:
        async with httpx.AsyncClient() as client:
            # 使用schema构造请求
            request = DeactivateUserRequest(user_id=user_id)
            req_body = request.dict()
            
            logging.info(f"[deactivate_user_api] 请求URL: {api_url}")
            logging.info(f"[deactivate_user_api] 请求体: {req_body}")
            
            resp = await client.post(api_url, json=req_body, timeout=5.0)
            logging.info(f"[deactivate_user_api] 响应状态: {resp.status_code}")
            logging.info(f"[deactivate_user_api] 响应内容: {resp.text}")
            
            if resp.status_code == 200:
                # 使用schema解析响应
                response_data = DeactivateUserResponse(**resp.json())
                logging.info(f"User deactivated: success={response_data.success}")
                return response_data.success
            else:
                return False
    except Exception as e:
        logging.error(f"deactivate_user_api error: {e}")
        return False

# 新增：回调数据常量
RESET_ACCOUNT = "reset_account"
CONFIRM_RESET_YES = "confirm_reset_yes"
CONFIRM_RESET_NO = "confirm_reset_no"

END_MESSAGE = "Hey there, welcome back! Your matches are waiting for you in the miniapp! Click the button below to check them out!"
APP_BUTTON = InlineKeyboardButton(
    "🎯 Open Cupid Lyra App",
     url="https://t.me/CupidLyraBot/app")
RESET_BUTTON = InlineKeyboardButton(
    "Reset my account",
     callback_data=RESET_ACCOUNT)

# 修改start函数


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message:
            return
        user_id = update.effective_user.id if update.effective_user else None
        if user_id:
            user_exists = await check_user_exists_by_telegram_id(user_id)
            if user_exists:
                # 已体验过，推送结束语和两个按钮
                keyboard = [
                    [APP_BUTTON],
                    [RESET_BUTTON]
                ]
                await update.message.reply_text(
                    END_MESSAGE,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                return
            
            # 没体验过，清理所有相关状态
            user_bots.pop(user_id, None)  # 安全删除
            user_stage.pop(user_id, None)
            user_gender_detected.pop(user_id, None)
            user_age.pop(user_id, None)
            user_target_gender.pop(user_id, None)
            telegram_to_user_id_map.pop(user_id, None)  # 清理映射
            logging.info(f"[start] 清理用户状态和映射 telegram_user_id {user_id}")
            
            # 自动设置用户为女性，目标性别为男性，但需要询问年龄
            telegram_user_name = update.effective_user.username if update.effective_user else None
            default_gender = 1  # 女性
            
            # 创建用户（默认女性）
            success = await create_or_update_user(user_id, telegram_user_name, default_gender)
            if not success:
                await update.message.reply_text("抱歉，创建用户失败，请稍后重试。")
                return
                
            # 保存用户性别（默认女性）
            user_gender_detected[user_id] = "female"
            await save_user_gender(user_id, "female")
            
            # 保存目标性别（默认男性）
            user_target_gender[user_id] = "men"
            await save_user_target_gender(user_id, "men")
            
            # 设置状态为等待年龄输入
            user_stage[user_id] = "awaiting_age"
            
            # 询问年龄
            await update.message.reply_text(Config.Bot.AGE_QUESTION_MESSAGE_FEMALE)
            
    except Exception as e:
        logging.error(f"Error in start(): {str(e)}")
        if update.message:
            await update.message.reply_text("抱歉，发生了错误，请稍后重试。")

# =================== 旧流程相关代码已注释 ===================
# 在 handle_message 里，性别选择、are you ready、waiting_ready等相关分支全部注释掉，仅保留AI对话主流程。
# ==========================================================


async def _keep_typing(bot, chat_id: int):
    """
    Keep showing typing indicator until cancelled.

    Args:
        bot: The bot instance
        chat_id (int): The chat ID to show typing in
    """
    while True:
        try:
            await bot.send_chat_action(chat_id=chat_id, action="typing")
            # Telegram typing indicator lasts ~5 seconds
            await asyncio.sleep(Config.Bot.TYPING_DURATION)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logging.error(f"Error in typing indicator: {str(e)}")
            break


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message or not update.message.text:
            return
        user_id = update.effective_user.id if update.effective_user else None
        if not user_id:
            return

        # 年龄输入阶段
        if user_stage.get(user_id) == "awaiting_age":
            try:
                age = int(update.message.text.strip())
                if 13 <= age <= 100:
                    user_age[user_id] = age
                    await save_user_age(user_id, age)
                    
                    # 年龄输入完成，直接进入AI对话阶段
                    user_stage[user_id] = "in_interview"
                    api_key = Config.API.GEMINI_API_KEY
                    if not api_key:
                        await update.message.reply_text(Config.Bot.ERROR_CONFIG_MESSAGE)
                        return
                        
                    user_bots[user_id] = MatchmakerBot(api_key, gender="female")
                    
                    # AI主动发起第一问
                    first_question = await user_bots[user_id].send_message_async("")
                    await update.message.reply_text(first_question)
                    return
                else:
                    await update.message.reply_text(Config.Bot.INVALID_AGE_MESSAGE)
                    return
            except ValueError:
                await update.message.reply_text(Config.Bot.INVALID_AGE_MESSAGE)
                return

        # AI对话阶段（原有逻辑）
        if user_id not in user_bots:
            api_key = Config.API.GEMINI_API_KEY
            if not api_key:
                await update.message.reply_text(Config.Bot.ERROR_CONFIG_MESSAGE)
                return
            user_gender = user_gender_detected.get(user_id, "female")  # 默认女性
            user_age_val = user_age.get(user_id, None)
            user_target_gender_val = user_target_gender.get(user_id, "men")  # 默认男性
            if user_age_val is None:  # 如果没有年龄信息，提示重新开始
                await update.message.reply_text("Please type /start to begin.")
                return
            user_bots[user_id] = MatchmakerBot(api_key, gender=user_gender)
            user_stage[user_id] = "in_interview"

        # AI 面试流程
        try:
            chat_id = update.effective_chat.id if update.effective_chat else None
            if not chat_id:
                return
            # Start typing indicator
            typing_task = asyncio.create_task(
                _keep_typing(context.bot, chat_id)
            )
            try:
                bot_instance = user_bots[user_id]
                # 确保用户输入是安全的UTF-8字符串
                user_text = update.message.text
                if user_text is None:
                    user_text = ""
                elif isinstance(user_text, bytes):
                    try:
                        user_text = user_text.decode('utf-8')
                    except UnicodeDecodeError:
                        user_text = user_text.decode('utf-8', errors='ignore')
                elif not isinstance(user_text, str):
                    user_text = str(user_text)

                response = await bot_instance.send_message_async(user_text)
                profile_keywords = [
                    "Your Ideal Partner Profile",
                    "Here is your ideal partner profile",
                    "Here's your ideal partner profile",
                    "Your ideal partner profile",
                    "Ideal Partner Profile",
                    "Partner Profile",
                    "Here is the profile",
                    "Here's the profile",
                    "The profile of your ideal partner",
                    "Your perfect match profile",
                    "Here is your perfect match",
                    "Your ideal match profile",
                    # 新增更宽泛的总结标志
                    "Here is a summary of the ideal partner profile we've uncovered together",
                    "Filter Questions",
                    "Ideal Partner",
                    "summary of the ideal partner profile",
                    "summary of your ideal partner profile",
                    "summary of your ideal partner",
                    "summary of the partner profile",
                    "summary of your partner profile"
                ]
                has_profile = any(keyword in response for keyword in profile_keywords)
                if has_profile:
                    # 立即存储完整AI总结到数据库
                    await save_user_personality_summary(user_id, response)
                    if "#end" not in response:
                        detected_keyword = next(keyword for keyword in profile_keywords if keyword in response)
                        logging.info(f"检测到最终总结，Profile关键词: '{detected_keyword}'，准备分割消息")
                        parts = bot_instance._split_final_summary(response)
                        logging.info(f"分割结果：{len(parts)} 部分")
                        if len(parts) == 2:
                            logging.info(f"成功分割，发送第一部分：{len(parts[0])} 字符")
                            await update.message.reply_text(parts[0])
                            await asyncio.sleep(1)
                            logging.info(f"发送第二部分：{len(parts[1])} 字符")
                            try:
                                await context.bot.send_message(chat_id=chat_id, text=parts[1])
                                user_final_string[user_id] = response  # 保存完整AI输出
                                user_filter_questions[user_id] = parts[1]  # 只保存筛选问题部分
                                session = get_session_from_mongodb(user_id)
                                gender = session.get('gender', '') if session and session.get('gender') else ''
                                started_at = user_started_at.get(user_id)
                                ended_at = None
                                save_final_session_to_mongodb(
                                    user_id=user_id,
                                    gender=gender,
                                    turns=user_turns.get(user_id, 0),
                                    started_at=started_at,
                                    ended_at=ended_at,
                                    final_string=response,
                                    filter_questions=parts[1],
                                    user_rating=-1
                                )
                                await asyncio.sleep(1)
                                # 直接发送结束语（带按钮）
                                await context.bot.send_message(
                                    chat_id=chat_id,
                                    text="Well, that brings our chat to a close! \nOh hold on! We have already got you a perfect match!",
                                    reply_markup=InlineKeyboardMarkup([
                                        [InlineKeyboardButton(text="🎯 Open Cupid Lyra App", url="https://t.me/CupidLyraBot/app")]
                                    ])
                                )
                                # 清理本轮内存会话状态（不清除User表数据）
                                for d in [
                                    user_bots,
                                    user_stage,
                                    user_gender_detected,
                                    user_age,
                                    user_target_gender,
                                    user_turns,
                                    user_started_at,
                                    user_final_string,
                                    user_filter_questions,
                                    user_waiting_rating
                                ]:
                                    d.pop(user_id, None)
                                return
                            except Exception as e:
                                logging.error(f"发送第二部分失败：{str(e)}")
                        else:
                            logging.info(f"分割失败，按原样发送")
                            await update.message.reply_text(response)
                            await context.bot.send_message(chat_id=chat_id, text="⚠️ 未能正确分割为两部分，请联系管理员。")
                            # 直接发送结束语（带按钮）
                            await context.bot.send_message(
                                chat_id=chat_id,
                                text="Well, that brings our chat to a close! \nOh hold on! We have already got you a perfect match!",
                                reply_markup=InlineKeyboardMarkup([
                                    [InlineKeyboardButton(text="🎯 Open Cupid Lyra App", url="https://t.me/CupidLyraBot/app")]
                                ])
                            )
                            # 清理本轮内存会话状态（不清除User表数据）
                            for d in [
                                user_bots,
                                user_stage,
                                user_gender_detected,
                                user_age,
                                user_target_gender,
                                user_turns,
                                user_started_at,
                                user_final_string,
                                user_filter_questions,
                                user_waiting_rating
                            ]:
                                d.pop(user_id, None)
                            return
                    else:
                        logging.info(f"未检测到#end，按原样发送")
                        await update.message.reply_text(response)
                else:
                    await update.message.reply_text(response)

                # 检查是否结束对话，如果是则保存最终总结
                if Config.Bot.END_TAG in response:
                    # 保存最终总结到用户表
                    await save_user_personality_summary(user_id, response)
                    # 保留原有的sessions表保存用于兼容
                    save_gemini_response_to_mongodb(user_id, response)

                    bot_instance.clear_history()
                    user_bots.pop(user_id, None)
                    user_stage.pop(user_id, None)
                    user_gender_detected.pop(user_id, None)
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=Config.Bot.VIEW_MALE_ANSWERS_MESSAGE,
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton(text=Config.Bot.VIEW_MALE_ANSWERS_BUTTON, url=Config.Bot.BOT_WEBAPP_URL)]
                        ])
                    )
            finally:
                typing_task.cancel()
                try:
                    await typing_task
                except asyncio.CancelledError:
                    pass
            # ========== 新增：每轮对话都存储会话快照 ==========
            session = get_session_from_mongodb(user_id)
            gender = session.get('gender', '') if session and session.get('gender') else ''
            started_at = user_started_at.get(user_id)
            ended_at = None  # 未结束
            # 可选：存完整历史
            history = None
            if hasattr(bot_instance, 'message_history'):
                history = bot_instance.message_history
            # 未到最后一轮，final_string/filter_questions/user_rating 均为 None
            sessions_collection.update_one(
                {'_id': user_id},
                {
                    '$set': {
                        'gender': gender,
                        'turns': user_turns.get(user_id, 0),
                        'started_at': started_at,
                        'ended_at': ended_at,
                        'last_user_message': update.message.text,
                        'last_bot_message': response,
                        'message_history': history,
                        'final_string': None,
                        'filter_questions': None,
                        'user_rating': -1  # 未评分时明确为-1
                    }
                },
                upsert=True
            )
        except Exception as e:
            logging.error(f"Error processing message for user {user_id}: {str(e)}")
            await update.message.reply_text(Config.Bot.ERROR_PROCESSING_MESSAGE)

        # 评分后除非/start，否则提示本轮已结束
        if user_id not in user_bots and user_stage.get(user_id) not in ["awaiting_age"]:
            if update.message.text.strip().lower() == "/start":
                await start(update, context)
            else:
                await update.message.reply_text("This round is over. Please type /start to begin a new experience.")
            return
    except Exception as e:
        logging.error(f"Error in handle_message(): {str(e)}")
        if update.message:
            await update.message.reply_text("抱歉，发生了错误，请稍后重试。")

# 新增：回调处理函数，监听reset按钮
async def reset_account_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        user_id = query.from_user.id
        await query.answer()
        # 弹出确认消息和Yes/No按钮
        keyboard = [
            [InlineKeyboardButton("Yes", callback_data=CONFIRM_RESET_YES), InlineKeyboardButton("No", callback_data=CONFIRM_RESET_NO)]
        ]
        await query.edit_message_text(
            "Are you sure you want to reset your account? All your matches and informations will be gone! There is no way back!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        logging.error(f"Error in reset_account_callback(): {str(e)}")
        if update.callback_query:
            await update.callback_query.edit_message_text("抱歉，发生了错误，请稍后重试。")

# 新增：回调处理函数，监听Yes/No按钮
async def confirm_reset_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        user_id = query.from_user.id
        await query.answer()
        if query.data == CONFIRM_RESET_YES:
            # 先获取映射的user_id
            if user_id in telegram_to_user_id_map:
                api_user_id = telegram_to_user_id_map[user_id]
                # 调用后端接口删除用户数据
                success = await deactivate_user_api(api_user_id)
                if success:
                    # 清理本地映射
                    telegram_to_user_id_map.pop(user_id, None)
                    logging.info(f"[confirm_reset_callback] 成功删除用户并清理映射 telegram_user_id {user_id}")
                    await query.edit_message_text("Your account has been removed. Type /start to create new profile!")
                else:
                    await query.edit_message_text("Failed to reset your profile. Please try again later.")
            else:
                # 没有映射，可能用户不存在，但仍然提示成功
                logging.warning(f"[confirm_reset_callback] telegram_user_id {user_id} 没有映射，可能用户不存在")
                await query.edit_message_text("Your account has been removed. Type /start to create new profile!")
        elif query.data == CONFIRM_RESET_NO:
            # 回到结束语和两个按钮
            keyboard = [
                [APP_BUTTON],
                [RESET_BUTTON]
            ]
            await query.edit_message_text(
                END_MESSAGE,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    except Exception as e:
        logging.error(f"Error in confirm_reset_callback(): {str(e)}")
        if update.callback_query:
            await update.callback_query.edit_message_text("抱歉，发生了错误，请稍后重试。")

# 注册回调处理器
application = None  # 你原有的ApplicationBuilder实例
if __name__ == "__main__":
    # Test MongoDB connection before starting the bot
    if not test_mongodb_connection():
        logging.error("Failed to connect to MongoDB. Please check your credentials and connection settings.")
        exit(1)

    # Validate configuration
    if not Config.validate_config():
        logging.error("Configuration validation failed. Please check your environment variables.")
        exit(1)

    # 配置网络连接设置
    import httpx
    from telegram.request import HTTPXRequest

    # 创建自定义的HTTP请求客户端，增加超时和重试设置
    # 增加连接池大小，减少超时时间，避免连接池耗尽
    request = HTTPXRequest(
        connection_pool_size=16,  # 增加连接池大小
        connect_timeout=15.0,     # 减少连接超时
        read_timeout=15.0,        # 减少读取超时
        write_timeout=15.0,       # 减少写入超时
        pool_timeout=10.0,        # 减少池超时，避免长时间等待
    )

    # 构建应用时使用自定义请求客户端
    application = ApplicationBuilder().token(Config.API.TELEGRAM_BOT_TOKEN).request(request).build()

    start_handler = CommandHandler('start', start)
    message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)

    application.add_handler(start_handler)
    application.add_handler(message_handler)
    application.add_handler(CallbackQueryHandler(reset_account_callback, pattern=f"^{RESET_ACCOUNT}$"))
    application.add_handler(CallbackQueryHandler(confirm_reset_callback, pattern=f"^{CONFIRM_RESET_YES}$|^{CONFIRM_RESET_NO}$"))

    # 添加错误处理和重试逻辑
    logging.info("正在启动Telegram机器人...")
    logging.info(f"使用Token: {Config.API.TELEGRAM_BOT_TOKEN[:10]}...")

    # 网络连接诊断
    def test_network_connectivity():
        """测试网络连接"""
        import subprocess
        import socket

        # 测试DNS解析
        try:
            socket.gethostbyname("api.telegram.org")
            logging.info("✅ DNS解析正常")
        except socket.gaierror:
            logging.error("❌ DNS解析失败，无法解析 api.telegram.org")
            return False

        # 测试网络连通性
        try:
            result = subprocess.run(['ping', '-c', '1', '-W', '5', '8.8.8.8'],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                logging.info("✅ 网络连通性正常")
            else:
                logging.error("❌ 网络连通性异常")
                return False
        except Exception as e:
            logging.error(f"❌ 网络测试失败: {str(e)}")
            return False

        return True

    # 执行网络诊断
    if not test_network_connectivity():
        logging.error("网络连接有问题，请检查网络设置或代理配置")
        logging.error("建议：")
        logging.error("1. 检查网络连接")
        logging.error("2. 配置代理服务器")
        logging.error("3. 检查防火墙设置")
        exit(1)

    try:
        # 尝试启动机器人，增加重试机制
        max_retries = 5  # 增加重试次数
        retry_count = 0

        while retry_count < max_retries:
            try:
                logging.info(f"尝试启动机器人 (第 {retry_count + 1} 次)")
                application.run_polling(
                    allowed_updates=Update.ALL_TYPES,
                    drop_pending_updates=True,
                    close_loop=False,
                    timeout=10,  # 添加轮询超时
                    bootstrap_retries=3  # 添加启动重试
                )
                break  # 如果成功启动，跳出循环
            except Exception as e:
                retry_count += 1
                logging.error(f"启动失败 (第 {retry_count} 次): {str(e)}")
                if retry_count < max_retries:
                    wait_time = min(5 * retry_count, 30)  # 递增等待时间，最大30秒
                    logging.info(f"等待 {wait_time} 秒后重试...")
                    import time
                    time.sleep(wait_time)
                else:
                    logging.error("所有重试都失败了，退出程序")
                    logging.error("可能的原因：")
                    logging.error("1. 网络连接问题")
                    logging.error("2. Telegram API 服务不可用")
                    logging.error("3. Bot Token 无效")
                    logging.error("4. 防火墙或代理阻止连接")
                    raise e

    except KeyboardInterrupt:
        logging.info("收到中断信号，正在关闭机器人...")
    except Exception as e:
        logging.error(f"机器人运行出错: {str(e)}")
        logging.error("请检查网络连接和Token是否正确")