# 语音转文字功能文档

## 概述

语音转文字功能是基于Whisper开源模型的语音识别系统，允许用户通过语音与AI进行交互。该功能完全遵循现有的三层架构设计，不会影响任何现有接口。

## 主要特性

- 🎤 **多格式支持**: 支持MP3, WAV, M4A, FLAC, OGG, AAC等常见音频格式
- 🌍 **多语言识别**: 支持中文、英文等多种语言，可自动检测语言
- 🤖 **AI集成**: 与现有的Gemini/Kimi AI服务无缝集成
- 📱 **RESTful API**: 提供标准的HTTP接口
- 🔒 **文件安全**: 自动验证文件格式和大小，防止恶意文件
- 🧹 **资源管理**: 自动清理临时文件，优化内存使用

## 快速开始

### 1. 安装依赖

```bash
# 激活虚拟环境
conda activate miracle_backend_env

# 安装必要的包
pip install openai-whisper pydub python-multipart
```

### 2. 配置环境变量

在`.env`文件中添加：

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

### 3. 测试功能

```bash
# 运行测试脚本
python test_voice_to_text.py

# 启动服务器
python app/server_run.py
```

### 4. 前端集成

```javascript
// 语音聊天示例
async function voiceChat(audioBlob, userId, gender = 'neutral') {
    const formData = new FormData();
    formData.append('audio_file', audioBlob);
    formData.append('user_id', userId);
    formData.append('gender', gender);
    
    const response = await fetch('/api/v1/voice/chat', {
        method: 'POST',
        body: formData
    });
    
    return await response.json();
}
```

## API接口

### 核心接口

1. **语音转文字**: `POST /api/v1/voice/transcribe`
   - 功能：将音频文件转换为文字
   - 参数：音频文件、用户ID、语言（可选）

2. **语音聊天**: `POST /api/v1/voice/chat` (推荐)
   - 功能：语音转文字 + AI回复
   - 参数：音频文件、用户ID、性别

3. **健康检查**: `GET /api/v1/voice/health`
   - 功能：检查服务状态

## 文档导航

### 📚 技术文档

- **[后端实现流程](./backend_implementation.md)** - 详细的后端架构和实现流程
- **[前端集成指南](./frontend_integration.md)** - 前端如何调用后端接口

### 🚀 使用指南

- **[快速开始](./README.md)** - 本文件，包含安装和配置说明
- **[API参考](./backend_implementation.md#接口设计)** - 完整的API接口说明

### 🔧 开发指南

- **[架构设计](./backend_implementation.md#系统架构)** - 系统架构和组件说明
- **[错误处理](./backend_implementation.md#错误处理策略)** - 错误处理和资源管理
- **[性能优化](./backend_implementation.md#性能优化)** - 性能优化建议

## 系统架构

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

## 数据流向

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

## 配置说明

### 模型大小选择

- **tiny**: 39MB，最快，准确率较低（开发测试推荐）
- **base**: 74MB，平衡速度和准确率（生产环境推荐）
- **small**: 244MB，较高准确率
- **medium**: 769MB，高准确率
- **large**: 1550MB，最高准确率，最慢

### 设备配置

- **CPU模式**: 适合大多数场景，兼容性好
- **GPU模式**: 如果有NVIDIA GPU，可显著提升处理速度

## 使用建议

### 开发阶段

1. 使用`tiny`模型快速测试功能
2. 使用HTML5原生版本验证接口
3. 关注日志输出和错误信息

### 生产环境

1. 使用`base`或`small`模型平衡性能和准确率
2. 使用React/Vue组件提供更好的用户体验
3. 实现完整的错误处理和用户反馈

### 性能优化

1. 音频时长控制在5分钟以内
2. 使用WAV格式获得最佳处理速度
3. 16kHz采样率通常足够使用

## 故障排除

### 常见问题

1. **Whisper模型加载失败**
   - 检查网络连接
   - 验证Python环境
   - 查看模型文件路径

2. **音频处理失败**
   - 检查pydub依赖
   - 验证ffmpeg安装
   - 确认音频文件格式

3. **服务启动失败**
   - 检查端口占用
   - 查看应用日志
   - 验证配置文件

### 日志查看

```bash
# 查看应用日志
tail -f logs/app.log

# 查看特定服务的日志
grep "VoiceToText" logs/app.log
```

## 技术支持

如果遇到问题，请：

1. 查看应用日志获取详细错误信息
2. 检查配置文件和环境变量
3. 运行测试脚本验证各组件状态
4. 在项目Issues中提交问题报告

## 更新日志

- **v1.0.0**: 初始版本，支持基本的语音转文字功能
  - 支持多种音频格式
  - 集成Whisper模型
  - 提供RESTful API接口
  - 与现有AI服务无缝集成

## 许可证

本项目遵循现有项目的许可证条款。

---

**注意**: 首次使用时会自动下载Whisper模型文件，请确保网络连接正常。
