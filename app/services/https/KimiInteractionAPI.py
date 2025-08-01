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
        检查是否是最终总结（基于新的Cupid Lushia输出格式）
        
        Args:
            response_text: AI响应文本
            
        Returns:
            bool: 是否是最终总结
        """
        # 检查是否包含新的总结关键词和结构标识
        summary_keywords = [
            # 标准格式标识
            "## 🌿 关键词提取",
            "### 关键词提取", 
            "关键词提取",
            "## 💖 你看重的关系特质",
            "### 你看重的关系特质",
            "你看重的关系特质",
            "## 🎯 提问问题包",
            "### 提问问题包",
            "提问问题包",
            
            # 相似表达
            "关键词总结",
            "关键词汇总",
            "关键词整理",
            "核心关键词",
            "重要关键词",
            "关键信息提取",
            "信息提取",
            "特质总结",
            "关系特质",
            "你的特质",
            "个人特质",
            "性格特质",
            "关系价值观",
            "你重视的",
            "你在意的",
            "你关注的",
            "你偏好的",
            
            # 问题包相关
            "现场问题",
            "约会问题",
            "交流问题",
            "聊天问题",
            "提问工具",
            "问题工具",
            "沟通工具",
            "对话工具",
            "你可以问",
            "你可以现场问",
            "可以问TA",
            "问对方",
            "询问对方",
            "了解对方",
            "探索对方",
            
            # Emoji标识
            "🌿 关键词",
            "💖 你看重",
            "💖 你重视",
            "💖 关系特质",
            "🎯 提问",
            "🎯 问题",
            "🎯 你可以",
            "🎯 现场问",
            "🎯 交流问题",
            
            # 生成语句
            "根据你分享的信息",
            "基于我们的对话",
            "通过刚才的交流",
            "从你的回答中",
            "我为你生成",
            "我为你整理",
            "我为你总结",
            "帮你整理了",
            "帮你生成了",
            "为你准备了",
            
            # 结束标识
            "对话总结",
            "探索完成",
            "分析完成",
            "整理完毕"
        ]
        
        response_lower = response_text.lower()
        return any(keyword.lower() in response_lower for keyword in summary_keywords)
    
    def _split_final_summary(self, response_text: str) -> list[str]:
        """
        分割最终总结为关键词摘要和问题包两部分
        
        Args:
            response_text: AI响应文本
            
        Returns:
            list[str]: [关键词摘要部分, 问题包部分]
        """
        # 寻找问题包的分割点
        lines = response_text.split('\n')
        keywords_summary_lines = []
        questions_lines = []
        in_questions = False
        
        for line in lines:
            # 检查是否到了问题包部分
            if any(keyword in line.lower() for keyword in [
                # 标准格式标识
                "## 🎯 提问问题包", "### 提问问题包", "提问问题包",
                "## 🎯 现场问题", "### 现场问题", "现场问题",
                
                # 相似表达
                "约会问题", "交流问题", "聊天问题", "提问工具", "问题工具",
                "沟通工具", "对话工具", "你可以问", "你可以现场问", "可以问ta",
                "问对方", "询问对方", "了解对方", "探索对方",
                
                # Emoji标识
                "🎯 提问", "🎯 问题", "🎯 你可以", "🎯 现场问", "🎯 交流问题",
                
                # 生成语句
                "现在，我将根据你分享的信息", "根据你分享的信息，我为你生成",
                "基于我们的对话，我为你", "通过刚才的交流，我为你",
                "从你的回答中，我为你", "我为你生成以下", "我为你整理了以下",
                "我为你总结了以下", "帮你整理了以下", "帮你生成了以下",
                "为你准备了以下", "以下是为你准备的", "以下是根据你的",
                
                # 问题引导语
                "以下三个问题", "三个问题", "这些问题", "问题列表",
                "建议问题", "推荐问题", "适合的问题"
            ]):
                in_questions = True
                questions_lines.append(line)
                continue
            
            if in_questions:
                questions_lines.append(line)
            else:
                keywords_summary_lines.append(line)
        
        # 构建两个部分
        keywords_summary = '\n'.join(keywords_summary_lines).strip()
        questions_part = '\n'.join(questions_lines).strip()
        
        # 如果没有找到问题包部分，尝试其他分割方式
        if not questions_part:
            # 方法1：寻找数字列表（1. 2. 3.）作为问题包的标识
            for i, line in enumerate(lines):
                if line.strip().startswith(('1.', '2.', '3.')) and '?' in line:
                    keywords_summary = '\n'.join(lines[:i]).strip()
                    questions_part = '\n'.join(lines[i:]).strip()
                    break
            
            # 方法2：如果仍然没有找到，寻找包含问题引导词的行
            if not questions_part:
                for i, line in enumerate(lines):
                    if any(keyword in line.lower() for keyword in [
                        "问题：", "问题:", "以下问题", "这些问题", "三个问题",
                        "适合的问题", "建议问题", "推荐问题", "现场问题"
                    ]):
                        keywords_summary = '\n'.join(lines[:i+1]).strip()
                        questions_part = '\n'.join(lines[i+1:]).strip()
                        break
        
        # 如果仍然没有找到分割点，返回原始消息
        if not questions_part:
            return [response_text]
        
        return [keywords_summary, questions_part]
    
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