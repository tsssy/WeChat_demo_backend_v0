#!/usr/bin/env python3
"""
性格卡片对象类
负责处理人格卡片的数据管理和业务逻辑
"""

from typing import List, Dict, Optional
from datetime import datetime
import pymongo
from app.core.database import get_db
from app.utils.my_logger import MyLogger

# 创建logger实例
logger = MyLogger("PersonalityCard")

class PersonalityCard:
    """性格卡片类"""
    
    def __init__(self):
        """初始化性格卡片对象"""
        self.db = get_db()
        self.collection = self.db["personality_cards"]  # MongoDB集合名称
        
    async def get_card_by_id(self, card_id: str) -> Optional[Dict]:
        """
        根据卡片ID获取卡片信息
        
        Args:
            card_id: 卡片ID (A1-A8)
            
        Returns:
            卡片信息字典，如果不存在则返回None
        """
        try:
            card = await self.collection.find_one({"card_id": card_id})
            if card:
                # 移除MongoDB的_id字段
                card.pop("_id", None)
            return card
        except Exception as e:
            logger.error(f"获取卡片失败 - card_id: {card_id}, error: {e}")
            return None
    
    async def get_all_cards(self) -> List[Dict]:
        """
        获取所有卡片信息
        
        Returns:
            所有卡片的列表
        """
        try:
            cursor = self.collection.find({}).sort("card_id", pymongo.ASCENDING)
            cards = await cursor.to_list(length=None)
            
            # 移除MongoDB的_id字段
            for card in cards:
                card.pop("_id", None)
                
            return cards
        except Exception as e:
            logger.error(f"获取所有卡片失败: {e}")
            return []
    
    async def get_cards_by_ids(self, card_ids: List[str]) -> List[Dict]:
        """
        根据卡片ID列表获取多张卡片
        
        Args:
            card_ids: 卡片ID列表
            
        Returns:
            卡片信息列表
        """
        try:
            cursor = self.collection.find(
                {"card_id": {"$in": card_ids}}
            ).sort("card_id", pymongo.ASCENDING)
            
            cards = await cursor.to_list(length=None)
            
            # 移除MongoDB的_id字段
            for card in cards:
                card.pop("_id", None)
                
            return cards
        except Exception as e:
            logger.error(f"批量获取卡片失败 - card_ids: {card_ids}, error: {e}")
            return []
    
    async def get_card_summary(self, card_id: str) -> Optional[Dict]:
        """
        获取卡片摘要信息（用于历史记录）
        
        Args:
            card_id: 卡片ID
            
        Returns:
            卡片摘要信息
        """
        try:
            card = await self.collection.find_one(
                {"card_id": card_id},
                {"card_id": 1, "card_name": 1, "emoji": 1, "_id": 0}
            )
            return card
        except Exception as e:
            logger.error(f"获取卡片摘要失败 - card_id: {card_id}, error: {e}")
            return None
    
    async def validate_card_exists(self, card_id: str) -> bool:
        """
        验证卡片是否存在
        
        Args:
            card_id: 卡片ID
            
        Returns:
            卡片是否存在
        """
        try:
            count = await self.collection.count_documents({"card_id": card_id})
            return count > 0
        except Exception as e:
            logger.error(f"验证卡片存在失败 - card_id: {card_id}, error: {e}")
            return False
    
    async def get_all_card_types(self) -> List[str]:
        """
        获取所有卡片类型ID
        
        Returns:
            所有卡片ID列表 (A1-A8)
        """
        try:
            cursor = self.collection.find({}, {"card_id": 1, "_id": 0}).sort("card_id", pymongo.ASCENDING)
            results = await cursor.to_list(length=None)
            return [result["card_id"] for result in results]
        except Exception as e:
            logger.error(f"获取卡片类型失败: {e}")
            return []
    
    async def get_card_count(self) -> int:
        """
        获取卡片总数
        
        Returns:
            卡片总数
        """
        try:
            count = await self.collection.count_documents({})
            return count
        except Exception as e:
            logger.error(f"获取卡片总数失败: {e}")
            return 0
    
    async def create_card(self, card_data: Dict) -> bool:
        """
        创建新卡片 (管理功能)
        
        Args:
            card_data: 卡片数据
            
        Returns:
            是否创建成功
        """
        try:
            card_data["created_at"] = datetime.now()
            result = await self.collection.insert_one(card_data)
            return result.inserted_id is not None
        except Exception as e:
            logger.error(f"创建卡片失败: {e}")
            return False
    
    async def bulk_create_cards(self, cards_data: List[Dict]) -> bool:
        """
        批量创建卡片 (初始化功能)
        
        Args:
            cards_data: 卡片数据列表
            
        Returns:
            是否创建成功
        """
        try:
            # 添加创建时间
            for card in cards_data:
                card["created_at"] = datetime.now()
            
            result = await self.collection.insert_many(cards_data)
            return len(result.inserted_ids) == len(cards_data)
        except Exception as e:
            logger.error(f"批量创建卡片失败: {e}")
            return False
    
    async def update_card(self, card_id: str, update_data: Dict) -> bool:
        """
        更新卡片信息 (管理功能)
        
        Args:
            card_id: 卡片ID
            update_data: 更新数据
            
        Returns:
            是否更新成功
        """
        try:
            update_data["updated_at"] = datetime.now()
            result = await self.collection.update_one(
                {"card_id": card_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"更新卡片失败 - card_id: {card_id}, error: {e}")
            return False
    
    async def search_cards_by_name(self, name_keyword: str) -> List[Dict]:
        """
        根据名称关键词搜索卡片
        
        Args:
            name_keyword: 名称关键词
            
        Returns:
            匹配的卡片列表
        """
        try:
            cursor = self.collection.find(
                {"card_name": {"$regex": name_keyword, "$options": "i"}}
            ).sort("card_id", pymongo.ASCENDING)
            
            cards = await cursor.to_list(length=None)
            
            # 移除MongoDB的_id字段
            for card in cards:
                card.pop("_id", None)
                
            return cards
        except Exception as e:
            logger.error(f"搜索卡片失败 - keyword: {name_keyword}, error: {e}")
            return [] 