import os
import asyncio
import aiohttp
from typing import List, Dict, Optional
from datetime import datetime
from app.config import settings
from app.utils.my_logger import MyLogger

logger = MyLogger("AIInteractionAPI")

class AIInteractionAPI:
    """AI交互API类，负责处理与豆包API的直接交互"""
    
    def __init__(self):
        self.api_key = "1e65c3d6-b827-4706-9fa8-93732bed0a8a"  # 豆包API Key
        self.model_name = "doubao-seed-1.6-250615"  # 豆包模型名称
        self.max_retries = 10
        self.base_url = "https://api.doubao.com/v1/chat/completions"
        
    def _get_system_prompt(self) -> str:
        """
        获取系统提示词
        
        Returns:
            str: 系统提示词内容
        """
        return """你是一个专业的AI助手，专门帮助用户进行情感咨询和关系指导。你的名字是Cupid Yukio。

你的主要职责：
1. 倾听用户的情感困扰和问题
2. 提供专业、温暖、有建设性的建议
3. 帮助用户更好地理解自己和他人
4. 在对话结束时提供总结和建议

请始终保持：
- 专业、温暖、理解的态度
- 具体、实用的建议
- 鼓励和支持的语气
- 对用户隐私的尊重

当对话达到自然结束点时，请提供总结和建议。"""
    
    def _format_history_for_api(self, history: List[tuple]) -> List[Dict[str, str]]:
        """
        将历史记录格式化为API需要的格式
        
        Args:
            history: List[Tuple[str, str, int, str]] 历史记录
                    格式: (消息内容, ISO时间字符串, 发送者ID, 显示名称)
        
        Returns:
            List[Dict[str, str]]: 格式化后的历史记录
        """
        formatted_history = []
        
        # 添加系统提示词
        system_prompt = self._get_system_prompt()
        formatted_history.append({
            "role": "user",
            "content": system_prompt
        })
        
        # 添加AI确认消息
        formatted_history.append({
            "role": "assistant",
            "content": "我理解了。我是Cupid Yukio，你的AI情感助手。我会倾听你的困扰，提供专业、温暖的建议。请告诉我你的问题。"
        })
        
        # 添加历史对话
        for message_content, timestamp, sender_id, display_name in history:
            if display_name == "I":  # 用户消息
                formatted_history.append({
                    "role": "user",
                    "content": message_content
                })
            else:  # AI消息 (display_name == "AI Assistant")
                formatted_history.append({
                    "role": "assistant",
                    "content": message_content
                })
        
        return formatted_history
    
    async def send_message_to_ai(self, user_id: int, message: str, history: list) -> dict:
        """
        向豆包API发送消息并获取响应
        
        Args:
            user_id: 用户ID
            message: 当前用户消息
            history: 历史消息列表 [Tuple[str, str, int, str]]
            
        Returns:
            dict: {
                "response": str,     # AI回复内容
                "status": str,      # "continue" 或 "end" 或 "error"
                "error": str,       # 如果失败，错误信息
                "metadata": dict    # 元数据
            }
        """
        try:
            # 1. 构建请求体
            messages = self._format_history_for_api(history)
            messages.append({"role": "user", "content": message})
            
            request_data = {
                "model": self.model_name,
                "messages": messages,
                "thinking": {
                    "type": "auto"  # 模型自行判断是否使用深度思考能力
                }
            }
            
            logger.info(f"向豆包API发送消息，用户ID: {user_id}, 消息长度: {len(message)}")
            
            # 2. 重试机制
            retry_count = 0
            while retry_count < self.max_retries:
                try:
                    # 3. 发送请求到豆包API
                    response = await self._make_api_request(request_data)
                    
                    # 4. 解析响应
                    response_text = response["choices"][0]["message"]["content"]
                    
                    logger.info(f"豆包API响应成功，用户ID: {user_id}, 响应长度: {len(response_text)}")
                    
                    # 5. 检查是否是最终总结
                    if self._is_final_summary(response_text):
                        # 分割总结
                        parts = self._split_final_summary(response_text)
                        return {
                            "response": response_text,
                            "status": "end",
                            "summary": {
                                "part1": parts[0] if len(parts) > 0 else "",
                                "part2": parts[1] if len(parts) > 1 else ""
                            },
                            "metadata": {
                                "tokens_used": response.get("usage", {}).get("total_tokens", 0),
                                "processing_time": response.get("processing_time", 0),
                                "model": self.model_name
                            }
                        }
                    else:
                        return {
                            "response": response_text,
                            "status": "continue",
                            "metadata": {
                                "tokens_used": response.get("usage", {}).get("total_tokens", 0),
                                "processing_time": response.get("processing_time", 0),
                                "model": self.model_name
                            }
                        }
                        
                except Exception as e:
                    retry_count += 1
                    logger.error(f"豆包API调用失败，用户ID: {user_id}, 重试次数: {retry_count}, 错误: {str(e)}")
                    
                    if retry_count >= self.max_retries:
                        logger.error(f"豆包API调用最终失败，用户ID: {user_id}, 已重试{self.max_retries}次")
                        return await self.get_fallback_response()
                    
                    # 指数退避
                    await asyncio.sleep(2 ** retry_count)
                    
        except Exception as e:
            logger.error(f"发送消息到AI失败，用户ID: {user_id}, 错误: {str(e)}")
            return await self.get_fallback_response()
    
    async def _make_api_request(self, request_data: dict) -> dict:
        """
        发送请求到豆包API
        
        Args:
            request_data: 请求数据
            
        Returns:
            dict: API响应
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        timeout = aiohttp.ClientTimeout(total=180)  # 3分钟超时
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                self.base_url,
                headers=headers,
                json=request_data
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"豆包API请求失败，状态码: {response.status}, 错误: {error_text}")
                
                return await response.json()
    
    def _is_final_summary(self, response_text: str) -> bool:
        """
        检查是否是最终总结
        
        Args:
            response_text: AI响应文本
            
        Returns:
            bool: 是否是最终总结
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
        return any(keyword in response_text for keyword in summary_keywords)
    
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
        logger.warning(f"总结分割失败，返回原文，用户ID: {response_text[:100]}...")
        return [response_text]
    
    async def get_fallback_response(self) -> dict:
        """
        获取备用响应
        
        Returns:
            dict: 备用响应
        """
        return {
            "response": "抱歉，我现在无法正常回复，请稍后再试。",
            "status": "error",
            "error": "API调用失败",
            "metadata": {
                "fallback_type": "api_error",
                "original_error": "API调用失败"
            }
        } 