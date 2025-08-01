#!/usr/bin/env python3
"""
性格测试系统的Pydantic数据模型
定义API请求和响应的数据结构
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# ===============================
# 基础数据模型
# ===============================

class QuestionOption(BaseModel):
    """题目选项模型"""
    option: str = Field(..., description="选项标识 (A/B/C/D)")
    text: str = Field(..., description="选项文本内容")
    personality_type: str = Field(..., description="对应的人格类型 (A1-A8)")

class PersonalityQuestion(BaseModel):
    """性格测试题目模型"""
    question_id: str = Field(..., description="题目ID (Q1-Q16)")
    question_text: str = Field(..., description="题目文本")
    options: List[QuestionOption] = Field(..., description="题目选项列表")

class VisualStyle(BaseModel):
    """视觉风格模型"""
    keywords: List[str] = Field(..., description="关键词列表")
    style: str = Field(..., description="风格描述")

class PersonalityCard(BaseModel):
    """人格卡片模型"""
    card_id: str = Field(..., description="卡片ID (A1-A8)")
    card_name: str = Field(..., description="卡片名称")
    title: str = Field(..., description="卡片标题")
    content: str = Field(..., description="卡片正文内容")
    emoji: str = Field(..., description="卡片表情符号")
    image_name: str = Field(..., description="图片文件名")
    visual_style: VisualStyle = Field(..., description="视觉风格指导")

class TestProgress(BaseModel):
    """测试进度模型"""
    current: int = Field(..., description="当前题目序号")
    total: int = Field(16, description="总题目数量")

class AnswerRecord(BaseModel):
    """答案记录模型"""
    question_id: str = Field(..., description="题目ID")
    selected_option: str = Field(..., description="选择的选项")
    personality_type: str = Field(..., description="对应的人格类型")

# ===============================
# API请求模型
# ===============================

class StartTestRequest(BaseModel):
    """开始测试请求模型"""
    user_id: int = Field(..., description="用户ID", example=12345)

class SubmitAnswerRequest(BaseModel):
    """提交答案请求模型"""
    session_id: str = Field(..., description="测试会话ID")
    question_id: str = Field(..., description="题目ID", example="Q1")
    selected_option: str = Field(..., description="选择的选项", example="B", pattern="^[ABCD]$")

# ===============================
# API响应模型
# ===============================

class StartTestResponse(BaseModel):
    """开始测试响应模型"""
    status: str = Field(..., description="响应状态")
    data: Optional[Dict[str, Any]] = Field(None, description="响应数据")
    error: Optional[str] = Field(None, description="错误信息")

class SubmitAnswerResponse(BaseModel):
    """提交答案响应模型"""
    status: str = Field(..., description="响应状态")
    data: Optional[Dict[str, Any]] = Field(None, description="响应数据")
    error: Optional[str] = Field(None, description="错误信息")

class TestResultResponse(BaseModel):
    """测试结果响应模型"""
    status: str = Field(..., description="响应状态")
    data: Optional[Dict[str, Any]] = Field(None, description="响应数据")
    error: Optional[str] = Field(None, description="错误信息")

class TestHistoryResponse(BaseModel):
    """测试历史响应模型"""
    status: str = Field(..., description="响应状态")
    data: Optional[Dict[str, Any]] = Field(None, description="响应数据")
    error: Optional[str] = Field(None, description="错误信息")

# ===============================
# 内部数据模型
# ===============================

class TestSession(BaseModel):
    """测试会话内部模型"""
    session_id: str = Field(..., description="会话ID")
    user_id: int = Field(..., description="用户ID")
    answers: List[AnswerRecord] = Field(default_factory=list, description="答案记录列表")
    scores: Dict[str, int] = Field(default_factory=dict, description="各人格类型得分")
    result_card: Optional[str] = Field(None, description="结果卡片ID")
    completed: bool = Field(False, description="是否完成测试")
    started_at: datetime = Field(default_factory=datetime.now, description="开始时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")

class TestHistoryItem(BaseModel):
    """测试历史项目模型"""
    session_id: str = Field(..., description="会话ID")
    result_card: Dict[str, str] = Field(..., description="结果卡片简要信息")
    completed_at: datetime = Field(..., description="完成时间") 