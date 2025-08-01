#!/usr/bin/env python3
"""
性格测试记录对象类
负责处理测试会话记录的数据管理和业务逻辑
"""

from typing import List, Dict, Optional
from datetime import datetime
import uuid
import pymongo
from app.core.database import get_db
from app.utils.my_logger import MyLogger

# 创建logger实例
logger = MyLogger("PersonalityTestRecord")

class PersonalityTestRecord:
    """性格测试记录类"""
    
    def __init__(self):
        """初始化性格测试记录对象"""
        self.db = get_db()
        self.collection = self.db["personality_test_records"]  # MongoDB集合名称
        
    async def create_test_session(self, user_id: int) -> Optional[str]:
        """
        创建新的测试会话
        
        Args:
            user_id: 用户ID
            
        Returns:
            会话ID，创建失败返回None
        """
        try:
            session_id = str(uuid.uuid4())
            session_data = {
                "session_id": session_id,
                "user_id": user_id,
                "answers": [],
                "scores": {},
                "result_card": None,
                "completed": False,
                "started_at": datetime.now(),
                "completed_at": None
            }
            
            result = await self.collection.insert_one(session_data)
            if result.inserted_id:
                return session_id
            return None
        except Exception as e:
            logger.error(f"创建测试会话失败 - user_id: {user_id}, error: {e}")
            return None
    
    async def get_test_session(self, session_id: str) -> Optional[Dict]:
        """
        获取测试会话信息
        
        Args:
            session_id: 会话ID
            
        Returns:
            会话信息字典，如果不存在则返回None
        """
        try:
            session = await self.collection.find_one({"session_id": session_id})
            if session:
                session.pop("_id", None)
            return session
        except Exception as e:
            logger.error(f"获取测试会话失败 - session_id: {session_id}, error: {e}")
            return None
    
    async def add_answer(self, session_id: str, question_id: str, selected_option: str, personality_type: str) -> bool:
        """
        添加答案到测试会话
        
        Args:
            session_id: 会话ID
            question_id: 题目ID
            selected_option: 选择的选项
            personality_type: 对应的人格类型
            
        Returns:
            是否添加成功
        """
        try:
            answer_record = {
                "question_id": question_id,
                "selected_option": selected_option,
                "personality_type": personality_type
            }
            
            result = await self.collection.update_one(
                {"session_id": session_id},
                {"$push": {"answers": answer_record}}
            )
            
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"添加答案失败 - session_id: {session_id}, question_id: {question_id}, error: {e}")
            return False
    
    async def update_scores(self, session_id: str, scores: Dict[str, int]) -> bool:
        """
        更新测试得分
        
        Args:
            session_id: 会话ID
            scores: 各人格类型得分字典
            
        Returns:
            是否更新成功
        """
        try:
            result = await self.collection.update_one(
                {"session_id": session_id},
                {"$set": {"scores": scores}}
            )
            
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"更新得分失败 - session_id: {session_id}, error: {e}")
            return False
    
    async def complete_test(self, session_id: str, result_card: str) -> bool:
        """
        完成测试，设置结果卡片
        
        Args:
            session_id: 会话ID
            result_card: 结果卡片ID
            
        Returns:
            是否完成成功
        """
        try:
            result = await self.collection.update_one(
                {"session_id": session_id},
                {
                    "$set": {
                        "result_card": result_card,
                        "completed": True,
                        "completed_at": datetime.now()
                    }
                }
            )
            
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"完成测试失败 - session_id: {session_id}, result_card: {result_card}, error: {e}")
            return False
    
    async def get_test_progress(self, session_id: str) -> Optional[Dict]:
        """
        获取测试进度
        
        Args:
            session_id: 会话ID
            
        Returns:
            进度信息 {current: int, total: int}
        """
        try:
            session = await self.collection.find_one(
                {"session_id": session_id},
                {"answers": 1, "_id": 0}
            )
            
            if session:
                current = len(session.get("answers", []))
                return {
                    "current": current,
                    "total": 16
                }
            return None
        except Exception as e:
            logger.error(f"获取测试进度失败 - session_id: {session_id}, error: {e}")
            return None
    
    async def is_test_completed(self, session_id: str) -> bool:
        """
        检查测试是否已完成
        
        Args:
            session_id: 会话ID
            
        Returns:
            测试是否已完成
        """
        try:
            session = await self.collection.find_one(
                {"session_id": session_id},
                {"completed": 1, "_id": 0}
            )
            
            return session.get("completed", False) if session else False
        except Exception as e:
            logger.error(f"检查测试完成状态失败 - session_id: {session_id}, error: {e}")
            return False
    
    async def get_user_test_history(self, user_id: int, limit: int = 10) -> List[Dict]:
        """
        获取用户测试历史记录
        
        Args:
            user_id: 用户ID
            limit: 返回记录数量限制
            
        Returns:
            历史记录列表
        """
        try:
            cursor = self.collection.find(
                {"user_id": user_id, "completed": True},
                {
                    "session_id": 1,
                    "result_card": 1,
                    "completed_at": 1,
                    "_id": 0
                }
            ).sort("completed_at", pymongo.DESCENDING).limit(limit)
            
            records = await cursor.to_list(length=None)
            return records
        except Exception as e:
            logger.error(f"获取用户测试历史失败 - user_id: {user_id}, error: {e}")
            return []
    
    async def get_user_test_count(self, user_id: int) -> int:
        """
        获取用户测试总次数
        
        Args:
            user_id: 用户ID
            
        Returns:
            测试总次数
        """
        try:
            count = await self.collection.count_documents(
                {"user_id": user_id, "completed": True}
            )
            return count
        except Exception as e:
            logger.error(f"获取用户测试次数失败 - user_id: {user_id}, error: {e}")
            return 0
    
    async def delete_test_session(self, session_id: str) -> bool:
        """
        删除测试会话 (管理功能)
        
        Args:
            session_id: 会话ID
            
        Returns:
            是否删除成功
        """
        try:
            result = await self.collection.delete_one({"session_id": session_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"删除测试会话失败 - session_id: {session_id}, error: {e}")
            return False
    
    async def cleanup_incomplete_sessions(self, hours_ago: int = 24) -> int:
        """
        清理未完成的测试会话 (维护功能)
        
        Args:
            hours_ago: 多少小时前的未完成会话需要清理
            
        Returns:
            清理的会话数量
        """
        try:
            cutoff_time = datetime.now() - datetime.timedelta(hours=hours_ago)
            
            result = await self.collection.delete_many({
                "completed": False,
                "started_at": {"$lt": cutoff_time}
            })
            
            deleted_count = result.deleted_count
            if deleted_count > 0:
                logger.info(f"清理了 {deleted_count} 个未完成的测试会话")
            
            return deleted_count
        except Exception as e:
            logger.error(f"清理未完成会话失败: {e}")
            return 0
    
    async def get_session_by_user_and_status(self, user_id: int, completed: bool) -> Optional[Dict]:
        """
        根据用户ID和完成状态获取最新的会话
        
        Args:
            user_id: 用户ID
            completed: 完成状态
            
        Returns:
            最新的会话信息
        """
        try:
            session = await self.collection.find_one(
                {"user_id": user_id, "completed": completed},
                sort=[("started_at", pymongo.DESCENDING)]
            )
            
            if session:
                session.pop("_id", None)
            return session
        except Exception as e:
            logger.error(f"获取用户会话失败 - user_id: {user_id}, completed: {completed}, error: {e}")
            return None 