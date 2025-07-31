"""
基于Kimi API的AI交互服务
提供重试机制、对话结束检测、总结分割等功能
"""

import os
import asyncio
import requests
from typing import List, Dict, Optional
from datetime import datetime
from app.config import settings
from app.utils.my_logger import MyLogger
from app.utils.prompt_manager import prompt_manager
import json

logger = MyLogger("KimiInteractionAPI")

class KimiInteractionAPI:
    """
    与Kimi AI模型进行交互的API封装
    提供完整的AI对话功能，包括重试机制、对话结束检测、总结分割等
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(KimiInteractionAPI, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, *args, **kwargs):
        # 从环境变量获取Kimi API配置
        self.api_key = os.getenv("KIMI_API_KEY", "sk-k6FqWbmEJJa9TKxK39fjCEflSG7JraFGlK2BnhAYcaHi89PJ")
        self.api_url = "https://api.moonshot.cn/v1/chat/completions"
        self.model_name = "moonshot-v1-8k"
        self.max_retries = 3  # 最大重试次数
        self.timeout = 60  # 请求超时时间（秒）
        
        if not self.api_key:
            logger.error("KIMI_API_KEY 未设置")
            raise ValueError("KIMI_API_KEY 未设置")

    def _get_system_prompt(self, gender: str = "neutral") -> str:
        """
        获取系统提示词
        
        Args:
            gender: 用户性别 ('male', 'female', 'neutral')
            
        Returns:
            str: 系统提示词内容
        """
        return prompt_manager.get_complete_prompt(gender)
    
    def _format_history_for_api(self, history: List[tuple], gender: str = "neutral") -> List[Dict[str, str]]:
        """
        将历史记录格式化为Kimi API需要的格式
        
        Args:
            history: List[Tuple[str, str, int, str]] 历史记录
                    格式: (消息内容, ISO时间字符串, 发送者ID, 显示名称)
            gender: 用户性别 ('male', 'female', 'neutral')
        
        Returns:
            List[Dict[str, str]]: 格式化后的历史记录
        """
        messages = []
        
        # 添加系统提示词
        messages.append({
            "role": "system",
            "content": self._get_system_prompt(gender)
        })
        
        # 添加历史对话
        for message_content, timestamp, sender_id, display_name in history:
            if display_name == "I":  # 用户消息
                messages.append({
                    "role": "user",
                    "content": message_content
                })
            else:  # AI消息 (display_name == "AI Assistant")
                messages.append({
                    "role": "assistant",
                    "content": message_content
                })
        
        return messages
    
    async def send_message_to_ai(self, user_id: int, message: str, history: list, gender: str = "neutral") -> dict:
        """
        向Kimi API发送消息并获取响应
        
        Args:
            user_id: 用户ID
            message: 用户消息
            history: 历史对话记录
            gender: 用户性别 ('male', 'female', 'neutral')
            
        Returns:
            dict: AI响应结果，包含以下字段：
                - success: bool - 是否成功
                - message: str - AI响应消息
                - summary: str - 总结内容（如果有）
                - is_final: bool - 是否是最终总结
                - timestamp: str - 时间戳
        """
        try:
            logger.info(f"[{user_id}] 开始处理用户消息: {message[:50]}...")
            
            # 格式化历史记录
            messages = self._format_history_for_api(history, gender)
            
            # 添加当前用户消息
            messages.append({
                "role": "user",
                "content": message
            })
            
            # 构建API请求数据（使用OpenAI兼容格式）
            request_data = {
                "model": self.model_name,
                "messages": messages,
                "stream": False,
                "temperature": 0.95,
                "top_p": 0.7,
                "max_tokens": 1024
            }
            
            # 发送API请求（包含重试机制）
            response_json = self._make_api_request(request_data, user_id)
            
            # 解析响应（OpenAI兼容格式）
            if 'choices' in response_json and len(response_json['choices']) > 0:
                choice = response_json['choices'][0]
                if 'message' in choice and 'content' in choice['message']:
                    # 提取AI响应文本
                    ai_response = choice['message']['content'].strip()
                    
                    # 检查是否是最终总结
                    if self._is_final_summary(ai_response):
                        summary_parts = self._split_final_summary(ai_response)
                        return {
                            "success": True,
                            "message": summary_parts[0] if summary_parts else ai_response,
                            "summary": summary_parts[1] if len(summary_parts) > 1 else "",
                            "is_final": True,
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        return {
                            "success": True,
                            "message": ai_response,
                            "summary": "",
                            "is_final": False,
                            "timestamp": datetime.now().isoformat()
                        }
                else:
                    raise Exception("API响应格式错误：缺少message或content")
            else:
                raise Exception("API响应格式错误：缺少choices")
                
        except Exception as e:
            logger.error(f"[{user_id}] 处理用户消息失败: {str(e)}", exc_info=True)
            return await self.get_fallback_response()
    
    def _make_api_request(self, request_data: dict, user_id: int) -> dict:
        """
        向Kimi API发送请求（包含重试机制）
        
        Args:
            request_data: 请求数据
            user_id: 用户ID
            
        Returns:
            dict: API响应
            
        Raises:
            Exception: 当所有重试都失败时抛出异常
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        logger.info(f"[{user_id}] 发送请求到Kimi API")
        
        # 重试机制
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                logger.info(f"[{user_id}] 尝试第 {retry_count + 1}/{self.max_retries} 次请求Kimi API...")
                
                response = requests.post(
                    self.api_url, 
                    json=request_data, 
                    headers=headers, 
                    timeout=self.timeout
                )
                
                logger.info(f"[{user_id}] 请求成功, 状态码: {response.status_code}")
                
                # 检查响应状态码
                if response.status_code == 200:
                    response_json = response.json()
                    logger.info(f"[{user_id}] AI响应成功")
                    logger.debug(f"[{user_id}] 完整响应: {json.dumps(response_json, indent=2, ensure_ascii=False)}")
                    return response_json
                else:
                    # 其他错误
                    response.raise_for_status()
                    
            except Exception as e:
                retry_count += 1
                logger.error(f"[{user_id}] Kimi API调用失败 (尝试 {retry_count}/{self.max_retries}), 错误: {str(e)}", exc_info=True)
                
                if retry_count >= self.max_retries:
                    logger.error(f"[{user_id}] Kimi API调用最终失败, 已达到最大重试次数 {self.max_retries}")
                    raise Exception(f"Kimi API调用最终失败, 已达到最大重试次数 {self.max_retries}")
                
                # 指数退避策略：2^retry_count秒
                sleep_time = 2 ** retry_count
                logger.info(f"[{user_id}] 等待 {sleep_time}秒后重试...")
                import time
                time.sleep(sleep_time)
                
        raise Exception("Kimi API调用最终失败, 已达到最大重试次数")
    
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
            "理想伴侣画像",
            "行动计划",
            "后续建议"
        ]
        
        response_lower = response_text.lower()
        return any(keyword.lower() in response_lower for keyword in summary_keywords)
    
    def _split_final_summary(self, response_text: str) -> list[str]:
        """
        分割最终总结为消息和总结两部分
        
        Args:
            response_text: AI响应文本
            
        Returns:
            list[str]: [消息, 总结]
        """
        # 分割逻辑：找到总结关键词，将其后的内容作为总结
        lines = response_text.split('\n')
        message_lines = []
        summary_lines = []
        in_summary = False
        
        for line in lines:
            # 检查是否包含总结关键词
            if any(keyword in line.lower() for keyword in [
                "总结", "总结报告", "建议总结", "对话总结", "最终建议", 
                "行动计划", "后续建议", "理想伴侣画像"
            ]):
                in_summary = True
            
            if in_summary:
                summary_lines.append(line)
            else:
                message_lines.append(line)
        
        message = '\n'.join(message_lines).strip()
        summary = '\n'.join(summary_lines).strip()
        
        # 如果没有找到总结部分，返回原始消息
        if not summary:
            return [response_text]
        
        return [message, summary]
    
    async def get_fallback_response(self) -> dict:
        """
        获取备用响应（当API调用失败时使用）
        
        Returns:
            dict: 备用响应
        """
        return {
            "success": True,
            "message": "抱歉，我现在遇到了一些技术问题。请稍后再试，或者重新开始对话。",
            "summary": "",
            "is_final": False,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _get_mock_response(self, user_id: int, message: str, history: list) -> dict:
        """
        获取模拟响应（用于测试）
        
        Args:
            user_id: 用户ID
            message: 用户消息
            history: 历史记录
            
        Returns:
            dict: 模拟响应
        """
        return {
            "success": True,
            "message": f"这是Kimi API的模拟响应。用户消息: {message}",
            "summary": "",
            "is_final": False,
            "timestamp": datetime.now().isoformat()
        } 