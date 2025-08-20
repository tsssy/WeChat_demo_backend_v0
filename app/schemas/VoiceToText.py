from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class VoiceTranscribeRequest(BaseModel):
    """语音转文字请求模型"""
    user_id: int = Field(..., description="用户ID", ge=1)
    language: Optional[str] = Field(None, description="语言代码，如zh-CN, en-US，留空则自动检测")

class VoiceTranscribeResponse(BaseModel):
    """语音转文字响应模型"""
    status: str = Field(..., description="响应状态")
    text: Optional[str] = Field(None, description="转换后的文字内容")
    confidence: Optional[float] = Field(None, description="识别置信度", ge=0.0, le=1.0)
    language: Optional[str] = Field(None, description="检测到的语言代码")
    processing_time: Optional[float] = Field(None, description="处理耗时（秒）")
    error: Optional[str] = Field(None, description="错误信息")

class VoiceChatRequest(BaseModel):
    """语音聊天请求模型"""
    user_id: int = Field(..., description="用户ID", ge=1)
    gender: Optional[str] = Field("neutral", description="用户性别，用于AI个性化回复")

class VoiceChatResponse(BaseModel):
    """语音聊天响应模型"""
    status: str = Field(..., description="响应状态")
    transcribed_text: Optional[str] = Field(None, description="用户说的话")
    ai_response: Optional[str] = Field(None, description="AI的回复内容")
    summary: Optional[str] = Field(None, description="总结信息")
    confidence: Optional[float] = Field(None, description="语音识别置信度")
    processing_time: Optional[float] = Field(None, description="总处理耗时（秒）")
    error: Optional[str] = Field(None, description="错误信息")

class AudioFileInfo(BaseModel):
    """音频文件信息模型"""
    filename: str = Field(..., description="文件名")
    file_size: int = Field(..., description="文件大小（字节）")
    duration: Optional[float] = Field(None, description="音频时长（秒）")
    format: str = Field(..., description="音频格式")
    sample_rate: Optional[int] = Field(None, description="采样率")
    channels: Optional[int] = Field(None, description="声道数")
