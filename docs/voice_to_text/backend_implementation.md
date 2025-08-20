# 语音转文字功能 - 后端接口实现流程

## 概述

本文档详细描述了语音转文字功能的后端实现流程，包括架构设计、数据流向、核心组件和实现细节。

## 系统架构

### 三层架构设计

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Layer     │    │  Schema Layer   │    │ Service Layer   │
│                 │    │                 │    │                 │
│ VoiceToText.py  │◄──►│ VoiceToText.py  │◄──►│VoiceToTextService│
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   HTTP Client   │    │  Data Models    │    │ AudioProcessor  │
│                 │    │                 │    │                 │
│   Requests      │    │   Validation    │    │   Whisper       │
│                 │    │                 │    │   Pydub         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 核心组件

1. **API层** (`app/api/v1/VoiceToText.py`)
   - 处理HTTP请求和响应
   - 参数验证和错误处理
   - 路由注册和管理

2. **Schema层** (`app/schemas/VoiceToText.py`)
   - 数据模型定义
   - 请求/响应结构
   - 数据验证规则

3. **Service层** (`app/services/https/VoiceToTextService.py`)
   - 业务逻辑处理
   - 音频处理协调
   - AI服务调用

4. **工具层** (`app/utils/audio_processor.py`)
   - 音频文件处理
   - Whisper模型管理
   - 文件格式转换

## 接口设计

### 1. 语音转文字接口

**接口地址**: `POST /api/v1/voice/transcribe`

**功能**: 将音频文件转换为文字

**请求参数**:
- `audio_file`: 音频文件（multipart/form-data）
- `user_id`: 用户ID（整数）
- `language`: 语言代码（可选，如zh-CN, en-US）

**响应结构**:
```json
{
    "status": "success",
    "text": "转换后的文字内容",
    "confidence": 0.95,
    "language": "zh-CN",
    "processing_time": 2.34,
    "error": null
}
```

### 2. 语音聊天接口

**接口地址**: `POST /api/v1/voice/chat`

**功能**: 语音转文字 + AI回复

**请求参数**:
- `audio_file`: 音频文件（multipart/form-data）
- `user_id`: 用户ID（整数）
- `gender`: 用户性别（可选，male/female/neutral）

**响应结构**:
```json
{
    "status": "success",
    "transcribed_text": "用户说的话",
    "ai_response": "AI的回复内容",
    "summary": "总结信息",
    "confidence": 0.95,
    "processing_time": 4.56,
    "error": null
}
```

### 3. 健康检查接口

**接口地址**: `GET /api/v1/voice/health`

**功能**: 检查服务状态

**响应结构**:
```json
{
    "status": "healthy",
    "service": "voice_to_text",
    "whisper_model_loaded": true,
    "supported_formats": [".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac"],
    "max_file_size_mb": 50.0
}
```

## 核心实现流程

### 语音聊天完整流程

```python
async def voice_chat(self, audio_file: UploadFile, user_id: int, gender: str = "neutral"):
    """语音聊天：语音转文字 + AI回复 + 保存对话记录"""
    
    start_time = time.time()
    temp_file_path = None
    converted_file_path = None
    
    try:
        # 步骤1: 保存上传的音频文件到本地临时目录
        temp_file_path = await self._save_uploaded_file(audio_file)
        logger.info(f"[{user_id}] 音频文件已保存到临时路径: {temp_file_path}")
        
        # 步骤2: 验证音频文件（本地验证）
        is_valid, error_msg = audio_processor.validate_audio_file(temp_file_path)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"音频文件验证失败: {error_msg}")
        
        # 步骤3: 获取音频文件信息
        audio_info = audio_processor.get_audio_info(temp_file_path)
        logger.info(f"[{user_id}] 音频文件信息: {audio_info}")
        
        # 步骤4: 转换为WAV格式（Whisper推荐使用WAV格式）
        converted_file_path = audio_processor.convert_to_wav(temp_file_path)
        logger.info(f"[{user_id}] 音频文件已转换为WAV格式: {converted_file_path}")
        
        # 步骤5: 调用Whisper模型将语音转为文字（本地AI模型）
        transcription_result = audio_processor.transcribe_audio(converted_file_path)
        transcribed_text = transcription_result["text"]
        logger.info(f"[{user_id}] 语音转文字完成: {transcribed_text[:50]}...")
        
        # 步骤6: 将转写的文字和提示词打包，调用现有的AI接口
        ai_response = await self._get_ai_response(user_id, transcribed_text, gender)
        
        # 步骤7: 计算总处理时间
        total_processing_time = time.time() - start_time
        
        # 步骤8: 构造响应结果
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
        # 步骤9: 清理本地临时文件
        if temp_file_path or converted_file_path:
            audio_processor.cleanup_temp_files(temp_file_path, converted_file_path)
```

### 详细步骤说明

#### 步骤1: 文件保存
```python
async def _save_uploaded_file(self, audio_file: UploadFile) -> str:
    """保存上传的文件到本地临时目录"""
    try:
        # 创建临时文件
        temp_file = tempfile.NamedTemporaryFile(
            delete=False, 
            suffix=os.path.splitext(audio_file.filename)[1]
        )
        temp_file_path = temp_file.name
        temp_file.close()
        
        # 读取上传文件内容并保存到本地
        content = await audio_file.read()
        with open(temp_file_path, "wb") as f:
            f.write(content)
        
        logger.info(f"上传文件已保存到临时路径: {temp_file_path}")
        return temp_file_path
        
    except Exception as e:
        logger.error(f"保存上传文件失败: {str(e)}")
        raise RuntimeError(f"无法保存上传文件: {str(e)}")
```

#### 步骤2: 文件验证
```python
def validate_audio_file(self, file_path: str) -> Tuple[bool, str]:
    """验证音频文件"""
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
            return False, "无法解码音频文件，文件可能损坏"
        
        return True, "文件验证通过"
        
    except Exception as e:
        logger.error(f"验证音频文件时发生错误: {str(e)}")
        return False, f"文件验证失败: {str(e)}"
```

#### 步骤3: 格式转换
```python
def convert_to_wav(self, input_path: str, output_path: Optional[str] = None) -> str:
    """将音频文件转换为WAV格式"""
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
```

#### 步骤4: Whisper转写
```python
def transcribe_audio(self, audio_path: str, language: Optional[str] = None) -> dict:
    """使用Whisper进行语音转文字"""
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
```

#### 步骤5: AI服务调用
```python
async def _get_ai_response(self, user_id: int, message: str, gender: str) -> Dict[str, Any]:
    """获取AI回复"""
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
            message=message,      # 转写后的文字
            history=history,      # 数据库中的历史记录
            gender=gender         # 用户性别
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
```

#### 步骤6: 资源清理
```python
def cleanup_temp_files(self, *file_paths: str):
    """清理临时文件"""
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"临时文件已删除: {file_path}")
        except Exception as e:
            logger.warning(f"删除临时文件失败: {file_path}, 错误: {str(e)}")
```

## 数据流向图

```
用户上传音频文件
        ↓
    保存到本地临时目录
        ↓
    本地验证和格式转换
        ↓
    调用Whisper模型（本地）
        ↓
    得到转写文字
        ↓
    调用现有AI接口（Gemini/Kimi）
        ↓
    得到AI回复
        ↓
    保存到数据库
        ↓
    清理本地临时文件
        ↓
    返回完整结果给前端
```

## 错误处理策略

### 1. 分层错误处理

```python
try:
    # 业务逻辑
    result = await voice_to_text_service.transcribe_audio_file(...)
    return response
except HTTPException:
    # 重新抛出HTTP异常，保持状态码
    raise
except Exception as e:
    # 捕获未预期的异常，转换为500错误
    logger.error(f"语音转文字接口发生未预期错误: {str(e)}")
    raise HTTPException(status_code=500, detail=f"语音转文字失败: {str(e)}")
```

### 2. 资源管理

```python
async def transcribe_audio_file(self, audio_file: UploadFile, user_id: int, language: Optional[str] = None):
    temp_file_path = None
    converted_file_path = None
    
    try:
        # 业务逻辑
        pass
    finally:
        # 确保资源清理
        if temp_file_path or converted_file_path:
            audio_processor.cleanup_temp_files(temp_file_path, converted_file_path)
```

## 性能优化

### 1. 模型单例模式

```python
class AudioProcessor:
    def __init__(self):
        self.whisper_model = None  # 延迟加载
        self._load_whisper_model()  # 初始化时加载
    
    def _load_whisper_model(self):
        # 从环境变量获取模型大小，默认为base
        model_size = os.getenv("WHISPER_MODEL_SIZE", "base")
        self.whisper_model = whisper.load_model(model_size)
```

### 2. 异步处理

```python
# 使用async/await处理文件上传和AI调用
async def voice_chat(self, audio_file: UploadFile, user_id: int, gender: str = "neutral"):
    # 异步处理音频文件
    temp_file_path = await self._save_uploaded_file(audio_file)
    
    # 异步调用AI服务
    ai_response = await self._get_ai_response(user_id, transcribed_text, gender)
```

### 3. 临时文件管理

```python
# 使用系统临时目录
temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file.filename)[1])
temp_file_path = temp_file.name

# 自动清理
finally:
    audio_processor.cleanup_temp_files(temp_file_path, converted_file_path)
```

## 配置说明

### 环境变量

```bash
# Whisper模型配置
WHISPER_MODEL_SIZE=base      # tiny, base, small, medium, large
WHISPER_DEVICE=cpu          # cpu, cuda

# 音频处理配置
MAX_AUDIO_FILE_SIZE=52428800 # 50MB
SUPPORTED_AUDIO_FORMATS=mp3,wav,m4a,flac,ogg,aac

# AI服务配置
CURRENT_AI_SERVICE=gemini    # gemini 或 kimi
```

### 模型大小说明

- **tiny**: 39MB，最快，准确率较低
- **base**: 74MB，平衡速度和准确率（推荐）
- **small**: 244MB，较高准确率
- **medium**: 769MB，高准确率
- **large**: 1550MB，最高准确率，最慢

## 监控和日志

### 1. 日志记录

```python
logger.info(f"[{user_id}] 开始处理音频文件: {audio_file.filename}")
logger.info(f"[{user_id}] 音频文件已保存到临时路径: {temp_file_path}")
logger.info(f"[{user_id}] 语音转文字完成: {transcribed_text[:50]}...")
logger.info(f"[{user_id}] 语音聊天处理完成，总耗时: {total_processing_time:.2f}秒")
```

### 2. 性能监控

- 处理时间：每个请求都会记录处理耗时
- 文件大小：记录上传文件的大小信息
- 识别准确率：Whisper提供的置信度分数

### 3. 健康检查

```python
@router.get("/health")
async def health_check():
    """健康检查接口"""
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
```

## 安全注意事项

1. **文件验证**: 自动验证文件格式和大小
2. **临时文件**: 处理完成后自动清理临时文件
3. **用户权限**: 建议在生产环境中添加用户认证
4. **文件存储**: 不永久存储用户上传的音频文件

## 故障排除

### 1. 模型加载失败
```bash
# 检查Python环境
python -c "import whisper; print('Whisper可用')"

# 检查模型文件
ls -la ~/.cache/whisper/
```

### 2. 音频处理失败
```bash
# 检查pydub依赖
python -c "from pydub import AudioSegment; print('Pydub可用')"

# 检查ffmpeg
ffmpeg -version
```

### 3. 服务启动失败
```bash
# 检查端口占用
lsof -i :8000

# 检查日志
tail -f logs/app.log
```

## 总结

语音转文字功能的后端实现采用了分层架构设计，通过本地音频处理、Whisper模型转写、现有AI服务调用和数据库存储的完整流程，实现了高效、可靠的语音交互功能。整个系统具有良好的错误处理、资源管理和性能优化特性。
