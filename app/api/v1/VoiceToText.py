"""
语音转文字API接口模块
提供语音识别和语音聊天的HTTP接口
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Optional
from app.schemas.VoiceToText import (
    VoiceTranscribeResponse, 
    VoiceChatResponse,
    VoiceTranscribeRequest,
    VoiceChatRequest
)
from app.services.https.VoiceToTextService import voice_to_text_service
from app.utils.my_logger import MyLogger

logger = MyLogger("VoiceToTextAPI")

router = APIRouter(prefix="/voice", tags=["语音转文字"])

@router.post("/transcribe", response_model=VoiceTranscribeResponse)
async def transcribe_audio(
    audio_file: UploadFile = File(..., description="音频文件"),
    user_id: int = Form(..., description="用户ID"),
    language: Optional[str] = Form(None, description="语言代码，如zh-CN, en-US，留空则自动检测")
):
    """
    语音转文字接口
    
    将用户上传的音频文件转换为文字
    
    Args:
        audio_file: 音频文件（支持mp3, wav, m4a, flac, ogg, aac格式）
        user_id: 用户ID
        language: 语言代码（可选）
        
    Returns:
        VoiceTranscribeResponse: 转写结果
        
    Raises:
        HTTPException: 400 - 文件格式不支持或文件损坏
        HTTPException: 500 - 服务器内部错误
    """
    try:
        logger.info(f"收到语音转文字请求: user_id={user_id}, filename={audio_file.filename}")
        
        # 验证文件类型（放宽：部分设备会上传 video/mp4 但仅含音轨）
        if not audio_file.content_type:
            raise HTTPException(status_code=400, detail="无法识别上传文件类型")
        if not (audio_file.content_type.startswith('audio/') or audio_file.content_type in [
            'video/mp4', 'video/quicktime'
        ]):
            raise HTTPException(status_code=400, detail="只支持音频文件（或仅含音轨的MP4/QuickTime）")
        
        # 调用服务层处理
        result = await voice_to_text_service.transcribe_audio_file(
            audio_file=audio_file,
            user_id=user_id,
            language=language
        )
        
        # 构造响应
        response = VoiceTranscribeResponse(
            status=result["status"],
            text=result["text"],
            confidence=result["confidence"],
            language=result["language"],
            processing_time=result["processing_time"],
            error=None
        )
        
        logger.info(f"语音转文字成功: user_id={user_id}, 文本长度={len(result['text'])}")
        return response
        
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        logger.error(f"语音转文字接口发生未预期错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"语音转文字失败: {str(e)}")

@router.post("/chat", response_model=VoiceChatResponse)
async def voice_chat(
    audio_file: UploadFile = File(..., description="音频文件"),
    user_id: int = Form(..., description="用户ID"),
    gender: str = Form("neutral", description="用户性别，用于AI个性化回复")
):
    """
    语音聊天接口
    
    将用户语音转换为文字，然后调用AI服务获取回复
    
    Args:
        audio_file: 音频文件（支持mp3, wav, m4a, flac, ogg, aac格式）
        user_id: 用户ID
        gender: 用户性别（male/female/neutral）
        
    Returns:
        VoiceChatResponse: 聊天结果，包含转写的文字和AI回复
        
    Raises:
        HTTPException: 400 - 文件格式不支持或文件损坏
        HTTPException: 500 - 服务器内部错误
    """
    try:
        logger.info(f"收到语音聊天请求: user_id={user_id}, filename={audio_file.filename}, gender={gender}")
        
        # 验证文件类型（放宽：部分设备会上传 video/mp4 但仅含音轨）
        if not audio_file.content_type:
            raise HTTPException(status_code=400, detail="无法识别上传文件类型")
        if not (audio_file.content_type.startswith('audio/') or audio_file.content_type in [
            'video/mp4', 'video/quicktime'
        ]):
            raise HTTPException(status_code=400, detail="只支持音频文件（或仅含音轨的MP4/QuickTime）")
        
        # 验证性别参数
        if gender not in ["male", "female", "neutral"]:
            raise HTTPException(status_code=400, detail="性别参数必须是 male, female 或 neutral")
        
        # 调用服务层处理
        result = await voice_to_text_service.voice_chat(
            audio_file=audio_file,
            user_id=user_id,
            gender=gender
        )
        
        # 构造响应
        response = VoiceChatResponse(
            status=result["status"],
            transcribed_text=result["transcribed_text"],
            ai_response=result["ai_response"],
            summary=result["summary"],
            confidence=result["confidence"],
            processing_time=result["processing_time"],
            error=None
        )
        
        logger.info(f"语音聊天成功: user_id={user_id}, AI回复长度={len(result['ai_response'])}")
        return response
        
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        logger.error(f"语音聊天接口发生未预期错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"语音聊天失败: {str(e)}")

@router.get("/health")
async def health_check():
    """
    健康检查接口
    
    检查语音转文字服务是否正常运行
    
    Returns:
        dict: 服务状态信息
    """
    try:
        # 检查Whisper模型是否已加载
        from app.utils.audio_processor import audio_processor
        model_loaded = audio_processor.whisper_model is not None
        
        return {
            "status": "healthy" if model_loaded else "unhealthy",
            "service": "voice_to_text",
            "whisper_model_loaded": model_loaded,
            "supported_formats": audio_processor.supported_formats,
            "max_file_size_mb": audio_processor.max_file_size / (1024 * 1024)
        }
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "voice_to_text",
            "error": str(e)
        }
