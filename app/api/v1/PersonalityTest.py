#!/usr/bin/env python3
"""
性格测试API路由
提供性格测试相关的RESTful API接口
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional
from app.schemas.PersonalityTest import (
    StartTestRequest, SubmitAnswerRequest,
    StartTestResponse, SubmitAnswerResponse, TestResultResponse, TestHistoryResponse
)
from app.services.https.PersonalityTestManager import PersonalityTestManager
from app.utils.my_logger import MyLogger

# 创建logger实例
logger = MyLogger("PersonalityTest")

# 创建路由器 - 抽卡游戏专用路由
router = APIRouter(
    prefix="/CardGame",
    tags=["Card Game", "抽卡游戏", "性格测试"],
    responses={
        400: {"description": "请求参数错误"},
        404: {"description": "资源不存在"},
        500: {"description": "服务器内部错误"}
    }
)

def get_personality_test_manager() -> PersonalityTestManager:
    """依赖注入：获取性格测试管理器实例"""
    return PersonalityTestManager()

@router.post("/start", response_model=StartTestResponse, summary="开始性格测试", description="创建新的性格测试会话并返回第一道题目")
async def start_personality_test(
    request: StartTestRequest,
    test_manager: PersonalityTestManager = Depends(get_personality_test_manager)
) -> StartTestResponse:
    """
    开始新的性格测试
    
    - **user_id**: 用户ID
    
    返回会话ID和第一道题目
    """
    try:
        logger.info(f"开始性格测试请求 - user_id: {request.user_id}")
        
        # 调用业务逻辑
        result = await test_manager.start_new_test(request.user_id)
        
        if not result:
            logger.error(f"开始测试失败 - user_id: {request.user_id}")
            return StartTestResponse(
                status="error",
                data=None,
                error="创建测试会话失败，请稍后重试"
            )
        
        logger.info(f"开始测试成功 - user_id: {request.user_id}, session_id: {result.get('session_id')}")
        
        return StartTestResponse(
            status="success",
            data=result,
            error=None
        )
        
    except Exception as e:
        logger.error(f"开始测试异常 - user_id: {request.user_id}, error: {e}", exc_info=True)
        return StartTestResponse(
            status="error",
            data=None,
            error="服务异常，请稍后重试"
        )

@router.post("/answer", response_model=SubmitAnswerResponse, summary="提交答案", description="提交题目答案并获取下一题或测试结果")
async def submit_answer(
    request: SubmitAnswerRequest,
    test_manager: PersonalityTestManager = Depends(get_personality_test_manager)
) -> SubmitAnswerResponse:
    """
    提交答案并获取下一题或测试结果
    
    - **session_id**: 测试会话ID
    - **question_id**: 题目ID (Q1-Q16)
    - **selected_option**: 选择的选项 (A/B/C/D)
    
    返回下一题目或测试完成结果
    """
    try:
        logger.info(f"提交答案请求 - session_id: {request.session_id}, question_id: {request.question_id}, option: {request.selected_option}")
        
        # 调用业务逻辑
        result = await test_manager.submit_answer(
            request.session_id,
            request.question_id,
            request.selected_option
        )
        
        if not result:
            logger.error(f"提交答案失败 - session_id: {request.session_id}")
            return SubmitAnswerResponse(
                status="error",
                data=None,
                error="提交答案失败，请检查会话是否有效"
            )
        
        logger.info(f"提交答案成功 - session_id: {request.session_id}")
        
        return SubmitAnswerResponse(
            status="success",
            data=result,
            error=None
        )
        
    except Exception as e:
        logger.error(f"提交答案异常 - session_id: {request.session_id}, error: {e}", exc_info=True)
        return SubmitAnswerResponse(
            status="error",
            data=None,
            error="服务异常，请稍后重试"
        )

@router.get("/result/{session_id}", response_model=TestResultResponse, summary="获取测试结果", description="根据会话ID获取性格测试结果")
async def get_test_result(
    session_id: str,
    test_manager: PersonalityTestManager = Depends(get_personality_test_manager)
) -> TestResultResponse:
    """
    获取测试结果
    
    - **session_id**: 测试会话ID
    
    返回完整的测试结果，包括性格卡片和得分详情
    """
    try:
        logger.info(f"获取测试结果请求 - session_id: {session_id}")
        
        # 调用业务逻辑
        result = await test_manager.get_test_result(session_id)
        
        if not result:
            logger.error(f"获取测试结果失败 - session_id: {session_id}")
            return TestResultResponse(
                status="error",
                data=None,
                error="测试结果不存在或测试尚未完成"
            )
        
        logger.info(f"获取测试结果成功 - session_id: {session_id}")
        
        return TestResultResponse(
            status="success",
            data=result,
            error=None
        )
        
    except Exception as e:
        logger.error(f"获取测试结果异常 - session_id: {session_id}, error: {e}", exc_info=True)
        return TestResultResponse(
            status="error",
            data=None,
            error="服务异常，请稍后重试"
        )

@router.get("/history/{user_id}", response_model=TestHistoryResponse, summary="获取测试历史", description="获取用户的性格测试历史记录")
async def get_test_history(
    user_id: int,
    limit: int = 10,
    test_manager: PersonalityTestManager = Depends(get_personality_test_manager)
) -> TestHistoryResponse:
    """
    获取用户测试历史记录
    
    - **user_id**: 用户ID
    - **limit**: 返回记录数量限制 (可选，默认10条)
    
    返回用户的历史测试记录列表
    """
    try:
        logger.info(f"获取测试历史请求 - user_id: {user_id}, limit: {limit}")
        
        # 验证参数
        if limit <= 0:
            limit = 10
        elif limit > 50:  # 限制最大返回数量
            limit = 50
        
        # 调用业务逻辑
        result = await test_manager.get_user_test_history(user_id, limit)
        
        if result is None:
            logger.error(f"获取测试历史失败 - user_id: {user_id}")
            return TestHistoryResponse(
                status="error",
                data=None,
                error="获取历史记录失败"
            )
        
        logger.info(f"获取测试历史成功 - user_id: {user_id}, count: {len(result.get('tests', []))}")
        
        return TestHistoryResponse(
            status="success",
            data=result,
            error=None
        )
        
    except Exception as e:
        logger.error(f"获取测试历史异常 - user_id: {user_id}, error: {e}", exc_info=True)
        return TestHistoryResponse(
            status="error",
            data=None,
            error="服务异常，请稍后重试"
        )

@router.get("/stats", summary="获取系统统计", description="获取性格测试系统的统计信息 (管理功能)")
async def get_system_stats(
    test_manager: PersonalityTestManager = Depends(get_personality_test_manager)
):
    """
    获取系统统计信息 (管理功能)
    
    返回题目数量、卡片数量等系统状态信息
    """
    try:
        logger.info("获取系统统计信息请求")
        
        # 调用业务逻辑
        stats = await test_manager.get_system_stats()
        
        logger.info(f"获取系统统计成功 - stats: {stats}")
        
        return {
            "status": "success",
            "data": stats,
            "error": None
        }
        
    except Exception as e:
        logger.error(f"获取系统统计异常: {e}", exc_info=True)
        return {
            "status": "error",
            "data": None,
            "error": "服务异常，请稍后重试"
        }

@router.delete("/cleanup", summary="清理过期会话", description="清理未完成的过期测试会话 (维护功能)")
async def cleanup_expired_sessions(
    hours_ago: int = 24,
    test_manager: PersonalityTestManager = Depends(get_personality_test_manager)
):
    """
    清理过期的未完成测试会话 (维护功能)
    
    - **hours_ago**: 清理多少小时前的会话 (可选，默认24小时)
    
    返回清理的会话数量
    """
    try:
        logger.info(f"清理过期会话请求 - hours_ago: {hours_ago}")
        
        # 验证参数
        if hours_ago <= 0:
            hours_ago = 24
        elif hours_ago > 168:  # 最多清理一周前的会话
            hours_ago = 168
        
        # 调用业务逻辑
        cleaned_count = await test_manager.cleanup_old_sessions(hours_ago)
        
        logger.info(f"清理过期会话成功 - 清理数量: {cleaned_count}")
        
        return {
            "status": "success",
            "data": {
                "cleaned_count": cleaned_count,
                "hours_ago": hours_ago
            },
            "error": None
        }
        
    except Exception as e:
        logger.error(f"清理过期会话异常: {e}", exc_info=True)
        return {
            "status": "error",
            "data": None,
            "error": "服务异常，请稍后重试"
        } 