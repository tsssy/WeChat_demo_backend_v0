from typing import List, Tuple, Optional, Dict
from datetime import datetime
import logging
from app.core.database import Database
from app.utils.my_logger import MyLogger

logger = MyLogger("AIResponseProcessor")

class AIResponseProcessor:
    """AI响应处理器类 - 单例模式"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.ai_chatrooms = {}  # user_id -> ai_message_id列表
            cls._instance.ai_messages = {}  # ai_message_id -> 消息详情
            cls._instance.ai_user_id = 999  # AI固定用户ID
            cls._instance.message_counter = 0  # 消息ID计数器
        return cls._instance
    
    async def initialize_counter(self):
        """
        从数据库初始化AI消息计数器，确保不会产生重复ID
        """
        if AIResponseProcessor._initialized:
            return
            
        try:
            # 查找数据库中最大的_id（ai_message_id存储在_id字段中）
            messages = await Database.find("AI_message", sort=[("_id", -1)], limit=1)
            
            if messages:
                max_id = messages[0]["_id"]
                self.message_counter = max_id
                logger.info(f"AI消息计数器从数据库初始化: 从 {max_id} 开始")
            else:
                self.message_counter = 0
                logger.info("未找到现有AI消息，从0开始计数")
                
            AIResponseProcessor._initialized = True
            
        except Exception as e:
            logger.error(f"初始化AI消息计数器失败: {e}")
            # 如果初始化失败，使用时间戳作为起始点以避免冲突
            import time
            self.message_counter = int(time.time() * 1000)  # 毫秒时间戳
            AIResponseProcessor._initialized = True
            logger.warning(f"使用时间戳作为AI消息计数器起始点: {self.message_counter}")
    
    async def initialize_from_database(self):
        """从数据库初始化AI聊天缓存 [内部方法，非API调用]"""
        if AIResponseProcessor._initialized:
            return
        
        try:
            # 首先初始化计数器
            await self.initialize_counter()
            
            logger.info("AIResponseProcessor: 开始从数据库加载AI聊天数据到内存")
            
            # 加载AI_chatroom数据
            chatrooms_data = await Database.find("AI_chatroom", {})
            loaded_chatrooms = 0
            
            for chatroom_data in chatrooms_data:
                user_id = chatroom_data.get("user_id")
                ai_message_ids = chatroom_data.get("ai_message_ids", [])
                if user_id:
                    self.ai_chatrooms[user_id] = ai_message_ids
                    loaded_chatrooms += 1
            
            # 加载AI_message数据
            messages_data = await Database.find("AI_message", {})
            loaded_messages = 0
            
            for message_data in messages_data:
                message_id = message_data.get("ai_message_id")
                if message_id:
                    self.ai_messages[message_id] = message_data
                    loaded_messages += 1
            
            AIResponseProcessor._initialized = True
            
            logger.info(f"AIResponseProcessor: 成功从数据库加载 {loaded_chatrooms} 个AI聊天室，{loaded_messages} 条消息到内存")
            logger.info(f"AIResponseProcessor: 当前内存中有 {len(self.ai_chatrooms)} 个聊天室，{len(self.ai_messages)} 条消息")
            
        except Exception as e:
            logger.error(f"AIResponseProcessor: 从数据库加载AI聊天数据失败: {str(e)}")
    
    async def get_conversation_history(self, user_id: int) -> List[Tuple[str, str, int, str]]:
        """
        获取对话历史记录 - 从内存中获取
        
        Args:
            user_id: 用户ID
            
        Returns:
            List[Tuple[str, str, int, str]]: 聊天历史列表
            格式: (消息内容, ISO时间字符串, 发送者ID, 显示名称)
        """
        try:
            # 1. 从内存中获取用户的AI聊天室数据
            if user_id not in self.ai_chatrooms:
                logger.info(f"用户 {user_id} 在内存中没有AI聊天记录")
                return []
            
            ai_message_ids = self.ai_chatrooms[user_id]
            if not ai_message_ids:
                logger.info(f"用户 {user_id} 在内存中的AI聊天记录为空")
                return []
            
            # 2. 从内存中获取消息详情
            messages = []
            for message_id in ai_message_ids:
                if message_id in self.ai_messages:
                    messages.append(self.ai_messages[message_id])
            
            # 3. 按时间排序
            messages.sort(key=lambda x: x.get("ai_message_send_time_in_utc", datetime.min))
            
            # 4. 格式化为前端需要的格式
            history = []
            for message in messages:
                content = message.get("ai_message_content", "")
                send_time = message.get("ai_message_send_time_in_utc", datetime.now())
                role = message.get("role", 0)
                
                # 格式化时间为ISO字符串
                if isinstance(send_time, datetime):
                    time_str = send_time.isoformat() + "Z"
                else:
                    time_str = str(send_time)
                
                # 根据role确定发送者ID和显示名称
                if role == 0:  # 用户消息
                    sender_id = user_id
                    display_name = "I"
                else:  # AI消息 (role == 1)
                    sender_id = self.ai_user_id
                    display_name = "AI Assistant"
                
                history.append((content, time_str, sender_id, display_name))
            
            logger.info(f"成功从内存获取用户 {user_id} 的AI聊天历史，共 {len(history)} 条记录")
            return history
            
        except Exception as e:
            logger.error(f"从内存获取用户 {user_id} 的AI聊天历史失败: {str(e)}")
            return []
    
    async def save_conversation_history(self, user_id: int, message: str, response: str) -> bool:
        """
        保存对话历史记录到内存
        
        Args:
            user_id: 用户ID
            message: 用户消息
            response: AI响应
            
        Returns:
            bool: 是否保存成功
        """
        try:
            # 确保计数器已初始化
            if not AIResponseProcessor._initialized:
                await self.initialize_counter()
            
            # 确保用户聊天室存在
            if user_id not in self.ai_chatrooms:
                self.ai_chatrooms[user_id] = []
            
            # 生成消息ID
            self.message_counter += 1
            user_message_id = self.message_counter
            
            self.message_counter += 1
            ai_message_id = self.message_counter
            
            # 保存用户消息到内存
            user_message_data = {
                "ai_message_id": user_message_id,
                "ai_message_content": message,
                "ai_message_send_time_in_utc": datetime.now(),
                "role": 0  # 用户消息
            }
            self.ai_messages[user_message_id] = user_message_data
            
            # 保存AI消息到内存
            ai_message_data = {
                "ai_message_id": ai_message_id,
                "ai_message_content": response,
                "ai_message_send_time_in_utc": datetime.now(),
                "role": 1  # AI消息
            }
            self.ai_messages[ai_message_id] = ai_message_data
            
            # 添加消息ID到聊天室
            self.ai_chatrooms[user_id].extend([user_message_id, ai_message_id])
            
            logger.info(f"成功保存用户 {user_id} 的对话历史到内存，消息ID: {user_message_id}, {ai_message_id}")
            return True
            
        except Exception as e:
            logger.error(f"保存用户 {user_id} 的对话历史失败: {str(e)}")
            return False
    
    async def check_conversation_end(self, response: str) -> bool:
        """
        检查对话是否结束
        
        Args:
            response: AI响应内容
            
        Returns:
            bool: 是否结束
        """
        # 这里先预留，后续实现结束检测功能
        return False
    
    async def check_conversation_end(self, response: str) -> bool:
        """
        检查对话是否结束
        
        Args:
            response: AI响应内容
            
        Returns:
            bool: 是否结束
        """
        # 检查是否包含总结关键词
        summary_keywords = [
            "总结",
            "总结报告", 
            "建议总结",
            "对话总结",
            "最终建议",
            "结束语",
            "#end",
            "Your Ideal Partner Profile",
            "理想伴侣画像"
        ]
        return any(keyword in response for keyword in summary_keywords)
    
    async def process_final_summary(self, response: str) -> dict:
        """
        处理最终总结
        
        Args:
            response: AI的最终响应
            
        Returns:
            dict: 总结信息
        """
        parts = self._split_final_summary(response)
        return {
            "status": "end",
            "summary": {
                "part1": parts[0] if len(parts) > 0 else "",
                "part2": parts[1] if len(parts) > 1 else ""
            }
        }
    
    def _split_final_summary(self, response_text: str) -> list[str]:
        """
        分割最终总结为两部分
        
        Args:
            response_text: AI响应文本
            
        Returns:
            list[str]: 分割后的两部分
        """
        import re
        
        # 1. 优先用 *** 分割
        split_match = re.search(r"\n?\s*\*\*\*\s*\n?", response_text, re.IGNORECASE)
        if split_match:
            split_pos = split_match.start()
            profile_part = response_text[:split_pos].strip()
            questions_part = response_text[split_match.end():].strip()
            return [profile_part, questions_part]
        
        # 2. 用关键词分割
        pattern = re.compile(
            r"(filter questions:?|筛选问题:?|问题工具包:?|提问建议:?|约会提问:?|推荐提问:?|建议提问:?|实用提问:?|情景提问:?|初期提问:?)",
            re.IGNORECASE
        )
        match = pattern.search(response_text)
        if match:
            split_pos = match.start()
            profile_part = response_text[:split_pos].strip()
            questions_part = response_text[split_pos:].strip()
            return [profile_part, questions_part]
        
        # 3. 兜底：返回原文
        logger.warning(f"总结分割失败，返回原文: {response_text[:100]}...")
        return [response_text]
    
    async def save_to_database(self, user_id: Optional[int] = None):
        """
        保存AI聊天数据到数据库
        如果指定了user_id，则保存该用户的聊天数据；如果没有指定，则保存所有内存中的聊天数据。
        [API调用]
        """
        try:
            if user_id is None:
                # 保存所有内存中的聊天数据
                success_count = 0
                total_chatrooms = len(self.ai_chatrooms)
                
                for user_id, message_ids in self.ai_chatrooms.items():
                    try:
                        # 保存聊天室数据
                        chatroom_data = {
                            "user_id": user_id,
                            "ai_message_ids": message_ids
                        }
                        
                        # 检查聊天室是否已在数据库中
                        existing_chatroom = await Database.find_one("AI_chatroom", {"user_id": user_id})
                        
                        if existing_chatroom:
                            # 如果存在，则更新
                            await Database.update_one(
                                "AI_chatroom",
                                {"user_id": user_id},
                                {"$set": {"ai_message_ids": message_ids}}
                            )
                        else:
                            # 如果不存在，则插入
                            await Database.insert_one("AI_chatroom", chatroom_data)
                        
                        success_count += 1
                        
                    except Exception as e:
                        logger.error(f"保存用户 {user_id} 的AI聊天室失败: {e}")
                        continue
                
                # 保存所有消息数据
                message_success_count = 0
                total_messages = len(self.ai_messages)
                
                for message_id, message_data in self.ai_messages.items():
                    try:
                        # 检查消息是否已在数据库中
                        existing_message = await Database.find_one("AI_message", {"ai_message_id": message_id})
                        
                        if existing_message:
                            # 如果存在，则更新
                            update_data = message_data.copy()
                            await Database.update_one(
                                "AI_message",
                                {"ai_message_id": message_id},
                                {"$set": update_data}
                            )
                        else:
                            # 如果不存在，则插入
                            await Database.insert_one("AI_message", message_data)
                        
                        message_success_count += 1
                        
                    except Exception as e:
                        logger.error(f"保存消息 {message_id} 失败: {e}")
                        continue
                
                logger.info(f"AI聊天数据保存完成: {success_count}/{total_chatrooms} 个聊天室, {message_success_count}/{total_messages} 条消息")
                return success_count == total_chatrooms and message_success_count == total_messages
                
            else:
                # 保存指定用户的聊天数据
                if user_id not in self.ai_chatrooms:
                    logger.warning(f"用户 {user_id} 在内存中没有AI聊天数据")
                    return False
                
                message_ids = self.ai_chatrooms[user_id]
                
                # 保存聊天室数据
                chatroom_data = {
                    "user_id": user_id,
                    "ai_message_ids": message_ids
                }
                
                existing_chatroom = await Database.find_one("AI_chatroom", {"user_id": user_id})
                
                if existing_chatroom:
                    await Database.update_one(
                        "AI_chatroom",
                        {"user_id": user_id},
                        {"$set": {"ai_message_ids": message_ids}}
                    )
                else:
                    await Database.insert_one("AI_chatroom", chatroom_data)
                
                # 保存该用户的所有消息
                for message_id in message_ids:
                    if message_id in self.ai_messages:
                        message_data = self.ai_messages[message_id]
                        existing_message = await Database.find_one("AI_message", {"ai_message_id": message_id})
                        
                        if existing_message:
                            await Database.update_one(
                                "AI_message",
                                {"ai_message_id": message_id},
                                {"$set": message_data}
                            )
                        else:
                            await Database.insert_one("AI_message", message_data)
                
                logger.info(f"用户 {user_id} 的AI聊天数据保存完成")
                return True
                
        except Exception as e:
            logger.error(f"保存AI聊天数据到数据库失败: {str(e)}")
            return False
    
    async def load_from_database(self):
        """
        从数据库加载数据到内存 [已废弃，使用initialize_from_database]
        """
        await self.initialize_from_database()
    
    def add_message_to_memory(self, user_id: int, message_id: int, message_data: dict):
        """
        添加消息到内存 [内部方法]
        
        Args:
            user_id: 用户ID
            message_id: 消息ID
            message_data: 消息数据
        """
        # 确保用户聊天室存在
        if user_id not in self.ai_chatrooms:
            self.ai_chatrooms[user_id] = []
        
        # 添加消息ID到聊天室
        if message_id not in self.ai_chatrooms[user_id]:
            self.ai_chatrooms[user_id].append(message_id)
        
        # 添加消息详情到内存
        self.ai_messages[message_id] = message_data
        
        logger.info(f"消息 {message_id} 已添加到用户 {user_id} 的内存中") 