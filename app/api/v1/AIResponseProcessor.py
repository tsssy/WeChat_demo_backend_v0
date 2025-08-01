from fastapi import APIRouter, Depends, HTTPException
from app.schemas.AIResponseProcessor import GetAIHistoryRequest, GetAIHistoryResponse, ChatRequest, ChatResponse
from app.services.https.AIResponseProcessor import AIResponseProcessor
from app.services.https.KimiInteractionAPI import KimiInteractionAPI
from app.utils.my_logger import MyLogger
import time

logger = MyLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI聊天"])

# 依赖注入工厂函数
def get_ai_processor():
    return AIResponseProcessor()

def get_ai_interaction():
    return KimiInteractionAPI()

@router.post("/history")
async def get_ai_chat_history(
    request: GetAIHistoryRequest,
    ai_processor: AIResponseProcessor = Depends(get_ai_processor)
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
    ai_interaction: KimiInteractionAPI = Depends(get_ai_interaction),
    ai_processor: AIResponseProcessor = Depends(get_ai_processor)
) -> ChatResponse:
    """
    统一的AI聊天处理入口
    """
    user_id = request.user_id
    logger.info(f"[{user_id}] 收到新的AI聊天请求: message='{request.message}'")
    try:
        # 1. 获取历史记录
        logger.info(f"[{user_id}] 步骤 1/4: 开始获取对话历史...")
        history = await ai_processor.get_conversation_history(user_id)
        logger.info(f"[{user_id}] 步骤 1/4: 获取到 {len(history)} 条历史记录")
        
        # 2. 发送到AI并获取响应
        logger.info(f"[{user_id}] 步骤 2/4: 开始调用KimiInteractionAPI.send_message_to_ai...")
        start_time = time.time()
        response = await ai_interaction.send_message_to_ai(
            user_id=user_id,
            message=request.message,
            history=history,
            gender="neutral"  # 添加gender参数
        )
        end_time = time.time()
        logger.info(f"[{user_id}] 步骤 2/4: AI响应成功，耗时: {end_time - start_time:.2f}秒, 成功: {response.get('success')}")
        
        # 3. 保存对话记录（如果成功）
        logger.info(f"[{user_id}] 步骤 3/4: 检查是否需要保存对话记录...")
        if response.get("success"):
            logger.info(f"[{user_id}] 步骤 3/4: 开始保存对话记录...")
            await ai_processor.save_conversation_history(
                user_id=user_id,
                message=request.message,
                response=response.get("message", "")  # 使用message字段
            )
            logger.info(f"[{user_id}] 步骤 3/4: 对话记录保存成功")
        else:
            logger.warning(f"[{user_id}] 步骤 3/4: AI响应失败，跳过保存")
        
        # 4. 返回响应
        logger.info(f"[{user_id}] 步骤 4/4: 准备向客户端返回最终响应...")
        # 构造响应
        if response.get("success"):
            chat_response = ChatResponse(
                status="success",
                response=response.get("message", ""),
                summary=response.get("summary", ""),
                error=None
            )
        else:
            chat_response = ChatResponse(
                status="error",
                response="",
                summary="",
                error="AI服务调用失败"
            )
        logger.info(f"[{user_id}] 步骤 4/4: 聊天请求处理完成")
        return chat_response
        
    except Exception as e:
        logger.error(f"[{user_id}] 处理AI聊天请求时发生未捕获异常: {str(e)}", exc_info=True)
        return ChatResponse(
            status="error",
            response="",
            summary="",
            error=f"处理聊天请求失败: {str(e)}"
        ) 