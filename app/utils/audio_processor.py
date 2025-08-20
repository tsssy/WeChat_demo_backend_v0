"""
音频处理工具模块
提供音频文件格式转换、验证、信息提取等功能
"""

import os
import tempfile
from typing import Optional, Tuple
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
import whisper
from app.utils.my_logger import MyLogger
from app.config import settings

logger = MyLogger("AudioProcessor")

class AudioProcessor:
    """音频处理工具类"""
    
    def __init__(self):
        """初始化音频处理器"""
        # 从配置读取支持的格式与大小限制
        configured_formats = getattr(settings, 'SUPPORTED_AUDIO_FORMATS', 'mp3,wav,m4a,flac,ogg,aac,mp4,webm')
        # 统一为以点开头的小写后缀
        self.supported_formats = [f".{ext.strip().lower()}" for ext in configured_formats.split(',') if ext.strip()]
        self.max_file_size = int(getattr(settings, 'MAX_AUDIO_FILE_SIZE', 50 * 1024 * 1024))
        self.whisper_model = None
        self._load_whisper_model()
    
    def _load_whisper_model(self):
        """加载Whisper模型"""
        try:
            # 从环境变量获取模型大小，默认为base
            model_size = os.getenv("WHISPER_MODEL_SIZE", "base")
            logger.info(f"正在加载Whisper模型: {model_size}")
            
            # 加载模型（首次加载会下载模型文件）
            self.whisper_model = whisper.load_model(model_size)
            logger.info(f"Whisper模型 {model_size} 加载成功")
            
        except Exception as e:
            logger.error(f"加载Whisper模型失败: {str(e)}")
            raise RuntimeError(f"无法加载Whisper模型: {str(e)}")
    
    def validate_audio_file(self, file_path: str) -> Tuple[bool, str]:
        """
        验证音频文件
        
        Args:
            file_path: 音频文件路径
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return False, "文件不存在"
            
            # 检查文件大小
            file_size = os.path.getsize(file_path)
            if file_size > self.max_file_size:
                return False, f"文件大小超过限制: {file_size / (1024*1024):.2f}MB > {self.max_file_size / (1024*1024)}MB"
            
            # 检查文件扩展名
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext not in self.supported_formats:
                return False, f"不支持的音频格式: {file_ext}，支持的格式: {', '.join(self.supported_formats)}"
            
            # 尝试加载音频文件
            try:
                audio = AudioSegment.from_file(file_path)
                if len(audio) == 0:
                    return False, "音频文件为空或损坏"
            except CouldntDecodeError:
                return False, "无法解码音频文件，可能缺少系统级 ffmpeg 编解码器或文件已损坏"
            
            return True, "文件验证通过"
            
        except Exception as e:
            logger.error(f"验证音频文件时发生错误: {str(e)}")
            return False, f"文件验证失败: {str(e)}"
    
    def get_audio_info(self, file_path: str) -> dict:
        """
        获取音频文件信息
        
        Args:
            file_path: 音频文件路径
            
        Returns:
            dict: 音频文件信息
        """
        try:
            audio = AudioSegment.from_file(file_path)
            
            info = {
                "filename": os.path.basename(file_path),
                "file_size": os.path.getsize(file_path),
                "duration": len(audio) / 1000.0,  # 转换为秒
                "format": os.path.splitext(file_path)[1][1:].upper(),
                "sample_rate": audio.frame_rate,
                "channels": audio.channels
            }
            
            return info
            
        except Exception as e:
            logger.error(f"获取音频信息失败: {str(e)}")
            raise RuntimeError(f"无法获取音频信息: {str(e)}")
    
    def convert_to_wav(self, input_path: str, output_path: Optional[str] = None) -> str:
        """
        将音频文件转换为WAV格式
        
        Args:
            input_path: 输入音频文件路径
            output_path: 输出WAV文件路径，如果为None则使用临时文件
            
        Returns:
            str: 输出WAV文件路径
        """
        try:
            # 加载音频文件
            audio = AudioSegment.from_file(input_path)
            
            # 如果没有指定输出路径，创建临时文件
            if output_path is None:
                temp_dir = tempfile.gettempdir()
                output_path = os.path.join(temp_dir, f"converted_{os.path.basename(input_path)}.wav")
            
            # 转换为WAV格式
            audio.export(output_path, format="wav")
            
            logger.info(f"音频文件转换成功: {input_path} -> {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"音频转换失败: {str(e)}")
            raise RuntimeError(f"音频转换失败: {str(e)}")
    
    def transcribe_audio(self, audio_path: str, language: Optional[str] = None) -> dict:
        """
        使用Whisper进行语音转文字
        
        Args:
            audio_path: 音频文件路径
            language: 语言代码，如果为None则自动检测
            
        Returns:
            dict: 转写结果，包含text, language, confidence等字段
        """
        try:
            if self.whisper_model is None:
                raise RuntimeError("Whisper模型未加载")
            
            logger.info(f"开始转写音频文件: {audio_path}")
            
            # 设置转写选项
            options = {}
            if language:
                options["language"] = language
                logger.info(f"使用指定语言: {language}")
            
            # 执行转写
            result = self.whisper_model.transcribe(audio_path, **options)
            
            # 提取结果
            transcription = {
                "text": result["text"].strip(),
                "language": result["language"],
                "confidence": result.get("avg_logprob", 0.0) if "avg_logprob" in result else None
            }
            
            logger.info(f"音频转写完成，语言: {transcription['language']}, 文本长度: {len(transcription['text'])}")
            return transcription
            
        except Exception as e:
            logger.error(f"音频转写失败: {str(e)}")
            raise RuntimeError(f"音频转写失败: {str(e)}")
    
    def cleanup_temp_files(self, *file_paths: str):
        """
        清理临时文件
        
        Args:
            *file_paths: 要删除的文件路径
        """
        for file_path in file_paths:
            try:
                if not file_path:
                    continue
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"临时文件已删除: {file_path}")
            except Exception as e:
                logger.warning(f"删除临时文件失败: {file_path}, 错误: {str(e)}")

# 创建全局实例
audio_processor = AudioProcessor()
