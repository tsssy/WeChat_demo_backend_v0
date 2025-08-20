# 语音转文字功能使用指南

## 功能概述

本项目新增了基于Whisper的语音转文字功能，允许用户通过语音与AI进行交互。该功能完全遵循现有的三层架构设计，不会影响任何现有接口。

## 主要特性

- 🎤 **多格式支持**: 支持MP3, WAV, M4A, FLAC, OGG, AAC等常见音频格式
- 🌍 **多语言识别**: 支持中文、英文等多种语言，可自动检测语言
- 🤖 **AI集成**: 与现有的Gemini/Kimi AI服务无缝集成
- 📱 **RESTful API**: 提供标准的HTTP接口
- 🔒 **文件安全**: 自动验证文件格式和大小，防止恶意文件
- 🧹 **资源管理**: 自动清理临时文件，优化内存使用

## API接口

### 1. 语音转文字接口

**接口地址**: `POST /api/v1/voice/transcribe`

**功能**: 将音频文件转换为文字

**请求参数**:
- `audio_file`: 音频文件（multipart/form-data）
- `user_id`: 用户ID（整数）
- `language`: 语言代码（可选，如zh-CN, en-US）

**响应示例**:
```json
{
    "status": "success",
    "text": "你好，我想了解一下这个产品",
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

**响应示例**:
```json
{
    "status": "success",
    "transcribed_text": "你好，我想了解一下这个产品",
    "ai_response": "你好！很高兴为你介绍我们的产品...",
    "summary": "用户询问产品信息",
    "confidence": 0.95,
    "processing_time": 4.56,
    "error": null
}
```

### 3. 健康检查接口

**接口地址**: `GET /api/v1/voice/health`

**功能**: 检查服务状态

**响应示例**:
```json
{
    "status": "healthy",
    "service": "voice_to_text",
    "whisper_model_loaded": true,
    "supported_formats": [".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac"],
    "max_file_size_mb": 50.0
}
```

## 配置说明

### 环境变量

在`.env`文件中添加以下配置：

```bash
# Whisper模型配置
WHISPER_MODEL_SIZE=base          # tiny, base, small, medium, large
WHISPER_DEVICE=cpu               # cpu, cuda

# 音频处理配置
MAX_AUDIO_FILE_SIZE=52428800     # 50MB
SUPPORTED_AUDIO_FORMATS=mp3,wav,m4a,flac,ogg,aac

# AI服务配置
CURRENT_AI_SERVICE=gemini        # gemini 或 kimi
```

### 模型大小说明

- **tiny**: 39MB，最快，准确率较低
- **base**: 74MB，平衡速度和准确率（推荐）
- **small**: 244MB，较高准确率
- **medium**: 769MB，高准确率
- **large**: 1550MB，最高准确率，最慢

## 使用示例

### Python客户端示例

```python
import requests

# 语音转文字
def transcribe_audio(audio_file_path, user_id, language=None):
    url = "http://localhost:8000/api/v1/voice/transcribe"
    
    with open(audio_file_path, 'rb') as f:
        files = {'audio_file': f}
        data = {'user_id': user_id}
        if language:
            data['language'] = language
            
        response = requests.post(url, files=files, data=data)
        return response.json()

# 语音聊天
def voice_chat(audio_file_path, user_id, gender="neutral"):
    url = "http://localhost:8000/api/v1/voice/chat"
    
    with open(audio_file_path, 'rb') as f:
        files = {'audio_file': f}
        data = {'user_id': user_id, 'gender': gender}
        
        response = requests.post(url, files=files, data=data)
        return response.json()

# 使用示例
if __name__ == "__main__":
    # 转写音频
    result = transcribe_audio("test.mp3", 123)
    print(f"转写结果: {result['text']}")
    
    # 语音聊天
    chat_result = voice_chat("test.mp3", 123, "male")
    print(f"AI回复: {chat_result['ai_response']}")
```

### JavaScript/HTML示例

```html
<!DOCTYPE html>
<html>
<head>
    <title>语音转文字测试</title>
</head>
<body>
    <h2>语音转文字测试</h2>
    
    <input type="file" id="audioFile" accept="audio/*">
    <input type="number" id="userId" placeholder="用户ID" value="123">
    <select id="gender">
        <option value="neutral">中性</option>
        <option value="male">男性</option>
        <option value="female">女性</option>
    </select>
    
    <button onclick="transcribeAudio()">转写音频</button>
    <button onclick="voiceChat()">语音聊天</button>
    
    <div id="result"></div>
    
    <script>
        async function transcribeAudio() {
            const file = document.getElementById('audioFile').files[0];
            const userId = document.getElementById('userId').value;
            
            if (!file) {
                alert('请选择音频文件');
                return;
            }
            
            const formData = new FormData();
            formData.append('audio_file', file);
            formData.append('user_id', userId);
            
            try {
                const response = await fetch('/api/v1/voice/transcribe', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                document.getElementById('result').innerHTML = `
                    <h3>转写结果:</h3>
                    <p><strong>文字:</strong> ${result.text}</p>
                    <p><strong>语言:</strong> ${result.language}</p>
                    <p><strong>置信度:</strong> ${result.confidence}</p>
                    <p><strong>处理时间:</strong> ${result.processing_time}秒</p>
                `;
            } catch (error) {
                alert('请求失败: ' + error.message);
            }
        }
        
        async function voiceChat() {
            const file = document.getElementById('audioFile').files[0];
            const userId = document.getElementById('userId').value;
            const gender = document.getElementById('gender').value;
            
            if (!file) {
                alert('请选择音频文件');
                return;
            }
            
            const formData = new FormData();
            formData.append('audio_file', file);
            formData.append('user_id', userId);
            formData.append('gender', gender);
            
            try {
                const response = await fetch('/api/v1/voice/chat', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                document.getElementById('result').innerHTML = `
                    <h3>聊天结果:</h3>
                    <p><strong>你说的话:</strong> ${result.transcribed_text}</p>
                    <p><strong>AI回复:</strong> ${result.ai_response}</p>
                    <p><strong>总结:</strong> ${result.summary}</p>
                    <p><strong>处理时间:</strong> ${result.processing_time}秒</p>
                `;
            } catch (error) {
                alert('请求失败: ' + error.message);
            }
        }
    </script>
</body>
</html>
```

## 性能优化建议

### 1. 模型选择
- 开发测试：使用`tiny`模型，加载快
- 生产环境：使用`base`或`small`模型，平衡性能和准确率
- 高精度需求：使用`medium`或`large`模型

### 2. 硬件优化
- CPU模式：适合大多数场景
- GPU模式：如果有NVIDIA GPU，可显著提升处理速度

### 3. 文件优化
- 音频时长：建议控制在5分钟以内
- 音频质量：16kHz采样率通常足够
- 文件格式：WAV格式处理最快

## 错误处理

### 常见错误及解决方案

1. **文件格式不支持**
   - 错误：`不支持的音频格式: .xxx`
   - 解决：转换为支持的格式（MP3, WAV, M4A等）

2. **文件过大**
   - 错误：`文件大小超过限制: XXMB > 50MB`
   - 解决：压缩音频文件或分段处理

3. **Whisper模型未加载**
   - 错误：`无法加载Whisper模型`
   - 解决：检查网络连接，确保模型下载成功

4. **AI服务调用失败**
   - 错误：`AI服务调用失败`
   - 解决：检查AI服务配置和网络连接

## 监控和日志

### 日志查看
```bash
# 查看应用日志
tail -f logs/app.log

# 查看特定服务的日志
grep "VoiceToText" logs/app.log
```

### 性能监控
- 处理时间：每个请求都会记录处理耗时
- 文件大小：记录上传文件的大小信息
- 识别准确率：Whisper提供的置信度分数

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

## 更新日志

- **v1.0.0**: 初始版本，支持基本的语音转文字功能
- 支持多种音频格式
- 集成Whisper模型
- 提供RESTful API接口
- 与现有AI服务无缝集成

## 技术支持

如果遇到问题，请：

1. 查看应用日志获取详细错误信息
2. 检查配置文件和环境变量
3. 运行测试脚本验证各组件状态
4. 在项目Issues中提交问题报告

---

**注意**: 首次使用时会自动下载Whisper模型文件，请确保网络连接正常。
