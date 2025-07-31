from pydantic import BaseModel, Field
from typing import List, Tuple, Optional
from datetime import datetime

class GetAIHistoryRequest(BaseModel):
    """获取AI聊天历史请求模型"""
    user_id: int = Field(..., description="用户ID", ge=1)

class GetAIHistoryResponse(BaseModel):
    """获取AI聊天历史响应模型"""
    status: str = Field(..., description="响应状态")
    data: List[Tuple[str, str, int, str]] = Field(..., description="聊天历史数据")
    error: Optional[str] = Field(None, description="错误信息")

class AIHistoryItem(BaseModel):
    """AI聊天历史单项模型"""
    message_content: str = Field(..., description="消息内容")
    message_send_time_in_utc: str = Field(..., description="ISO格式时间字符串")
    message_sender_id: int = Field(..., description="发送者ID")
    display_name: str = Field(..., description="显示名称") 

class ChatRequest(BaseModel):
    """AI聊天请求模型"""
    user_id: int = Field(..., description="用户ID", ge=1)
    message: str = Field(..., description="用户消息")

class ChatResponse(BaseModel):
    """AI聊天响应模型"""
    status: str = Field(..., description="响应状态")
    response: Optional[str] = Field(None, description="AI回复内容")
    summary: Optional[str] = Field(None, description="总结信息")
    error: Optional[str] = Field(None, description="错误信息") 