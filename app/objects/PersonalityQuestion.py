#!/usr/bin/env python3
"""
性格测试问题对象类
负责处理测试题目的数据管理和业务逻辑
"""

from typing import List, Dict, Optional
from datetime import datetime
import pymongo
from app.core.database import get_db
from app.utils.my_logger import MyLogger

# 创建logger实例
logger = MyLogger("PersonalityQuestion")

class PersonalityQuestion:
    """性格测试问题类"""
    
    def __init__(self):
        """初始化性格测试问题对象"""
        self.db = get_db()
        self.collection = self.db["personality_questions"]  # MongoDB集合名称
        
    async def get_question_by_id(self, question_id: str) -> Optional[Dict]:
        """
        根据题目ID获取题目信息
        
        Args:
            question_id: 题目ID (Q1-Q16)
            
        Returns:
            题目信息字典，如果不存在则返回None
        """
        try:
            question = await self.collection.find_one({"question_id": question_id})
            if question:
                # 移除MongoDB的_id字段
                question.pop("_id", None)
            return question
        except Exception as e:
            logger.error(f"获取题目失败 - question_id: {question_id}, error: {e}")
            return None
    
    async def get_all_questions(self) -> List[Dict]:
        """
        获取所有题目信息
        
        Returns:
            所有题目的列表
        """
        try:
            cursor = self.collection.find({}).sort("question_id", pymongo.ASCENDING)
            questions = await cursor.to_list(length=None)
            
            # 移除MongoDB的_id字段
            for question in questions:
                question.pop("_id", None)
                
            return questions
        except Exception as e:
            logger.error(f"获取所有题目失败: {e}")
            return []
    
    async def get_questions_by_range(self, start: int = 1, end: int = 16) -> List[Dict]:
        """
        获取指定范围的题目
        
        Args:
            start: 开始题目序号 (默认1)
            end: 结束题目序号 (默认16)
            
        Returns:
            指定范围的题目列表
        """
        try:
            question_ids = [f"Q{i}" for i in range(start, end + 1)]
            cursor = self.collection.find(
                {"question_id": {"$in": question_ids}}
            ).sort("question_id", pymongo.ASCENDING)
            
            questions = await cursor.to_list(length=None)
            
            # 移除MongoDB的_id字段
            for question in questions:
                question.pop("_id", None)
                
            return questions
        except Exception as e:
            logger.error(f"获取题目范围失败 - start: {start}, end: {end}, error: {e}")
            return []
    
    async def get_first_question(self) -> Optional[Dict]:
        """
        获取第一道题目
        
        Returns:
            第一道题目信息
        """
        return await self.get_question_by_id("Q1")
    
    async def get_next_question(self, current_question_id: str) -> Optional[Dict]:
        """
        获取下一道题目
        
        Args:
            current_question_id: 当前题目ID
            
        Returns:
            下一道题目信息，如果是最后一道则返回None
        """
        try:
            # 提取当前题目序号
            current_num = int(current_question_id[1:])  # 去掉'Q'前缀
            
            if current_num >= 16:
                return None  # 已经是最后一道题
            
            next_question_id = f"Q{current_num + 1}"
            return await self.get_question_by_id(next_question_id)
        except Exception as e:
            logger.error(f"获取下一题失败 - current: {current_question_id}, error: {e}")
            return None
    
    async def get_question_count(self) -> int:
        """
        获取题目总数
        
        Returns:
            题目总数
        """
        try:
            count = await self.collection.count_documents({})
            return count
        except Exception as e:
            logger.error(f"获取题目总数失败: {e}")
            return 0
    
    async def validate_answer(self, question_id: str, selected_option: str) -> bool:
        """
        验证答案是否有效
        
        Args:
            question_id: 题目ID
            selected_option: 选择的选项 (A/B/C/D)
            
        Returns:
            答案是否有效
        """
        try:
            question = await self.get_question_by_id(question_id)
            if not question:
                return False
            
            # 检查选项是否存在
            valid_options = [opt["option"] for opt in question.get("options", [])]
            return selected_option in valid_options
        except Exception as e:
            logger.error(f"验证答案失败 - question_id: {question_id}, option: {selected_option}, error: {e}")
            return False
    
    async def get_personality_type_by_answer(self, question_id: str, selected_option: str) -> Optional[str]:
        """
        根据答案获取对应的人格类型
        
        Args:
            question_id: 题目ID
            selected_option: 选择的选项
            
        Returns:
            对应的人格类型 (A1-A8)，无效答案返回None
        """
        try:
            question = await self.get_question_by_id(question_id)
            if not question:
                return None
            
            # 查找对应选项的人格类型
            for option in question.get("options", []):
                if option["option"] == selected_option:
                    return option["personality_type"]
            
            return None
        except Exception as e:
            logger.error(f"获取人格类型失败 - question_id: {question_id}, option: {selected_option}, error: {e}")
            return None
    
    async def create_question(self, question_data: Dict) -> bool:
        """
        创建新题目 (管理功能)
        
        Args:
            question_data: 题目数据
            
        Returns:
            是否创建成功
        """
        try:
            question_data["created_at"] = datetime.now()
            result = await self.collection.insert_one(question_data)
            return result.inserted_id is not None
        except Exception as e:
            logger.error(f"创建题目失败: {e}")
            return False
    
    async def bulk_create_questions(self, questions_data: List[Dict]) -> bool:
        """
        批量创建题目 (初始化功能)
        
        Args:
            questions_data: 题目数据列表
            
        Returns:
            是否创建成功
        """
        try:
            # 添加创建时间
            for question in questions_data:
                question["created_at"] = datetime.now()
            
            result = await self.collection.insert_many(questions_data)
            return len(result.inserted_ids) == len(questions_data)
        except Exception as e:
            logger.error(f"批量创建题目失败: {e}")
            return False 