"""
语音转文字服务模块
提供语音识别、AI聊天等核心业务功能
"""

import os
import tempfile
import time
from typing import Optional, Dict, Any
from fastapi import UploadFile, HTTPException
from app.utils.audio_processor import audio_processor
from app.services.https.GeminiInteractionAPI import GeminiInteractionAPI
from app.services.https.KimiInteractionAPI import KimiInteractionAPI
from app.config import settings
from app.utils.my_logger import MyLogger

logger = MyLogger("VoiceToTextService")

class VoiceToTextService:
    """语音转文字服务类"""
    
    def __init__(self):
        """初始化语音转文字服务"""
        self.ai_service = self._get_ai_service()
    
    def _get_ai_service(self):
        """根据配置获取AI服务实例"""
        service_name = getattr(settings, 'CURRENT_AI_SERVICE', 'gemini').lower().strip()
        if service_name == "gemini":
            return GeminiInteractionAPI()
        else:
            return KimiInteractionAPI()
    
    async def transcribe_audio_file(
        self, 
        audio_file: UploadFile, 
        user_id: int, 
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        转写音频文件为文字
        
        Args:
            audio_file: 上传的音频文件
            user_id: 用户ID
            language: 语言代码（可选）
            
        Returns:
            Dict[str, Any]: 转写结果
        """
        start_time = time.time()
        temp_file_path = None
        converted_file_path = None
        
        try:
            logger.info(f"[{user_id}] 开始处理音频文件: {audio_file.filename}")
            
            # 1. 保存上传的文件到临时目录
            temp_file_path = await self._save_uploaded_file(audio_file)
            logger.info(f"[{user_id}] 音频文件已保存到临时路径: {temp_file_path}")
            
            # 2. 验证音频文件
            is_valid, error_msg = audio_processor.validate_audio_file(temp_file_path)
            if not is_valid:
                raise HTTPException(status_code=400, detail=f"音频文件验证失败: {error_msg}")
            
            # 3. 获取音频文件信息
            audio_info = audio_processor.get_audio_info(temp_file_path)
            logger.info(f"[{user_id}] 音频文件信息: {audio_info}")
            
            # 4. 转换为WAV格式（Whisper推荐使用WAV格式）
            converted_file_path = audio_processor.convert_to_wav(temp_file_path)
            logger.info(f"[{user_id}] 音频文件已转换为WAV格式: {converted_file_path}")
            
            # 5. 执行语音转文字
            transcription_result = audio_processor.transcribe_audio(converted_file_path, language)
            logger.info(f"[{user_id}] 语音转文字完成: {transcription_result['text'][:50]}...")
            
            # 6. 计算处理时间
            processing_time = time.time() - start_time
            
            # 7. 构造响应结果
            result = {
                "status": "success",
                "text": transcription_result["text"],
                "confidence": transcription_result.get("confidence", 0.0),
                "language": transcription_result["language"],
                "processing_time": round(processing_time, 2),
                "audio_info": audio_info
            }
            
            logger.info(f"[{user_id}] 音频转写成功，耗时: {processing_time:.2f}秒")
            return result
            
        except HTTPException:
            # 重新抛出HTTP异常
            raise
        except Exception as e:
            logger.error(f"[{user_id}] 音频转写过程中发生错误: {str(e)}")
            raise HTTPException(status_code=500, detail=f"音频转写失败: {str(e)}")
        finally:
            # 清理临时文件
            if temp_file_path or converted_file_path:
                audio_processor.cleanup_temp_files(temp_file_path, converted_file_path)
    
    async def voice_chat(
        self, 
        audio_file: UploadFile, 
        user_id: int, 
        gender: str = "neutral"
    ) -> Dict[str, Any]:
        """
        语音聊天功能：语音转文字 + AI回复
        
        Args:
            audio_file: 上传的音频文件
            user_id: 用户ID
            gender: 用户性别
            
        Returns:
            Dict[str, Any]: 聊天结果
        """
        start_time = time.time()
        temp_file_path = None
        converted_file_path = None
        
        try:
            logger.info(f"[{user_id}] 开始语音聊天处理: {audio_file.filename}")
            
            # 1. 保存上传的文件到临时目录
            temp_file_path = await self._save_uploaded_file(audio_file)
            
            # 2. 验证音频文件
            is_valid, error_msg = audio_processor.validate_audio_file(temp_file_path)
            if not is_valid:
                raise HTTPException(status_code=400, detail=f"音频文件验证失败: {error_msg}")
            
            # 3. 转换为WAV格式
            converted_file_path = audio_processor.convert_to_wav(temp_file_path)
            
            # 4. 执行语音转文字
            transcription_result = audio_processor.transcribe_audio(converted_file_path)
            transcribed_text = transcription_result["text"]
            
            logger.info(f"[{user_id}] 语音转文字完成: {transcribed_text[:50]}...")
            
            # 5. 调用AI服务获取回复
            ai_response = await self._get_ai_response(user_id, transcribed_text, gender)
            
            # 6. 计算总处理时间
            total_processing_time = time.time() - start_time
            
            # 7. 构造响应结果
            result = {
                "status": "success",
                "transcribed_text": transcribed_text,
                "ai_response": ai_response.get("message", ""),
                "summary": ai_response.get("summary", ""),
                "confidence": transcription_result.get("confidence", 0.0),
                "processing_time": round(total_processing_time, 2),
                "language": transcription_result["language"]
            }
            
            logger.info(f"[{user_id}] 语音聊天处理完成，总耗时: {total_processing_time:.2f}秒")
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"[{user_id}] 语音聊天过程中发生错误: {str(e)}")
            raise HTTPException(status_code=500, detail=f"语音聊天失败: {str(e)}")
        finally:
            # 清理临时文件
            if temp_file_path or converted_file_path:
                audio_processor.cleanup_temp_files(temp_file_path, converted_file_path)
    
    async def _save_uploaded_file(self, audio_file: UploadFile) -> str:
        """
        保存上传的文件到临时目录
        
        Args:
            audio_file: 上传的文件
            
        Returns:
            str: 保存后的文件路径
        """
        try:
            # 创建临时文件
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file.filename)[1])
            temp_file_path = temp_file.name
            temp_file.close()
            
            # 读取上传文件内容并保存
            content = await audio_file.read()
            with open(temp_file_path, "wb") as f:
                f.write(content)
            
            logger.info(f"上传文件已保存到临时路径: {temp_file_path}")
            return temp_file_path
            
        except Exception as e:
            logger.error(f"保存上传文件失败: {str(e)}")
            raise RuntimeError(f"无法保存上传文件: {str(e)}")
    
    async def _get_ai_response(self, user_id: int, message: str, gender: str) -> Dict[str, Any]:
        """
        获取AI回复
        
        Args:
            user_id: 用户ID
            message: 用户消息
            gender: 用户性别
            
        Returns:
            Dict[str, Any]: AI回复结果
        """
        try:
            # 获取对话历史记录
            from app.services.https.AIResponseProcessor import AIResponseProcessor
            ai_processor = AIResponseProcessor()
            
            # 确保AI处理器已初始化
            await ai_processor.initialize_from_database()
            
            # 获取历史记录
            history = await ai_processor.get_conversation_history(user_id)
            logger.info(f"[{user_id}] 获取到 {len(history)} 条历史记录")
            
            # 调用AI服务获取回复
            response = await self.ai_service.send_message_to_ai(
                user_id=user_id,
                message=message,
                history=history,
                gender=gender
            )
            
            # 如果AI回复成功，保存对话记录
            if response.get("success"):
                await ai_processor.save_conversation_history(
                    user_id=user_id,
                    message=message,
                    response=response.get("message", "")
                )
                logger.info(f"[{user_id}] 语音聊天对话记录已保存")
            
            return response
            
        except Exception as e:
            logger.error(f"[{user_id}] 获取AI回复失败: {str(e)}")
            raise RuntimeError(f"AI服务调用失败: {str(e)}")

# 创建全局实例
voice_to_text_service = VoiceToTextService()
