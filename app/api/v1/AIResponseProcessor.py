from fastapi import APIRouter, Depends, HTTPException
from app.schemas.AIResponseProcessor import GetAIHistoryRequest, GetAIHistoryResponse, ChatRequest, ChatResponse
from app.services.https.AIResponseProcessor import AIResponseProcessor
from app.services.https.AIInteractionAPI import AIInteractionAPI
from app.utils.my_logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/ai", tags=["AI聊天"])

@router.post("/history")
async def get_ai_chat_history(
    request: GetAIHistoryRequest,
    ai_processor: AIResponseProcessor = Depends()
) -> GetAIHistoryResponse:
    """
    获取AI聊天历史记录
    
    Args:
        request: 获取历史请求
        ai_processor: AI响应处理器
        
    Returns:
        GetAIHistoryResponse: 聊天历史响应
    """
    try:
        logger.info(f"开始获取用户 {request.user_id} 的AI聊天历史")
        
        # 调用service层获取历史记录
        history_data = await ai_processor.get_conversation_history(request.user_id)
        
        # 构造响应
        response = GetAIHistoryResponse(
            status="success",
            data=history_data,
            error=None
        )
        
        logger.info(f"成功获取用户 {request.user_id} 的AI聊天历史，共 {len(history_data)} 条记录")
        return response
        
    except Exception as e:
        logger.error(f"获取用户 {request.user_id} 的AI聊天历史失败: {str(e)}")
        
        # 返回错误响应
        return GetAIHistoryResponse(
            status="error",
            data=[],
            error=f"获取聊天历史失败: {str(e)}"
        )

@router.post("/chat")
async def handle_ai_chat(
    request: ChatRequest,
    ai_interaction: AIInteractionAPI = Depends(),
    ai_processor: AIResponseProcessor = Depends()
) -> ChatResponse:
    """
    统一的AI聊天处理入口
    """
    try:
        logger.info(f"开始处理用户 {request.user_id} 的AI聊天请求")
        
        # 1. 获取历史记录
        history = await ai_processor.get_conversation_history(request.user_id)
        logger.info(f"获取到用户 {request.user_id} 的历史记录，共 {len(history)} 条")
        
        # 2. 发送到AI并获取响应
        response = await ai_interaction.send_message_to_ai(
            user_id=request.user_id,
            message=request.message,
            history=history
        )
        
        logger.info(f"AI响应成功，用户ID: {request.user_id}, 状态: {response['status']}")
        
        # 3. 保存对话记录（如果不是错误状态）
        if response["status"] != "error":
            await ai_processor.save_conversation_history(
                user_id=request.user_id,
                message=request.message,
                response=response["response"]
            )
            logger.info(f"对话记录保存成功，用户ID: {request.user_id}")
        
        # 4. 返回响应
        return ChatResponse(
            status=response["status"],
            response=response.get("response"),
            summary=response.get("summary"),
            error=response.get("error")
        )
        
    except Exception as e:
        logger.error(f"处理AI聊天请求失败，用户ID: {request.user_id}, 错误: {str(e)}")
        return ChatResponse(
            status="error",
            error=f"处理聊天请求失败: {str(e)}"
        ) 