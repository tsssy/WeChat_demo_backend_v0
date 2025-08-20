# WeChat Demo Backend v0

一个基于 FastAPI 的微信演示后端服务，支持用户管理、匹配系统、聊天室和AI交互等功能。

## 🚀 主要功能

### 核心功能
- **用户管理**: 用户注册、登录、信息管理
- **匹配系统**: 智能用户匹配算法
- **聊天室**: 实时聊天和消息管理
- **AI交互**: 集成 Gemini 和 Kimi AI 服务
- **语音转文字**: 支持多种音频格式的语音识别

### 新增功能
- **语音转文字**: 使用 OpenAI Whisper 模型
- **语音聊天**: 语音输入 + AI 回复
- **多格式支持**: MP3, WAV, M4A, FLAC, OGG, AAC, MP4, WebM

## 🛠️ 技术栈

- **后端框架**: FastAPI
- **数据库**: MongoDB
- **AI服务**: Google Gemini, Moonshot Kimi
- **语音识别**: OpenAI Whisper
- **音频处理**: pydub + ffmpeg
- **WebSocket**: 实时通信
- **部署**: Nginx + Uvicorn

## 📦 快速开始

### 1. 环境要求
- Python 3.8+
- MongoDB
- ffmpeg (用于音频处理)

### 2. 安装依赖

#### 自动安装 (推荐)
```bash
# 克隆项目
git clone <repository-url>
cd WeChat_demo_backend_v0

# 运行安装脚本
./install_voice_deps.sh
```

#### 手动安装
```bash
# 创建虚拟环境
conda create -n miracle_backend_env python=3.11
conda activate miracle_backend_env

# 安装系统依赖
conda install -c conda-forge ffmpeg

# 安装 Python 依赖
pip install -r requirements.txt
```

### 3. 配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置
vim .env
```

### 4. 启动服务
```bash
# 启动后端服务
python app/server_run.py

# 或使用 uvicorn
uvicorn app.server_run:app --host 0.0.0.0 --port 8000
```

## 🎤 语音功能使用

### API 接口

#### 语音转文字
```http
POST /api/v1/voice/transcribe
Content-Type: multipart/form-data

audio_file: [音频文件]
user_id: [用户ID]
language: [语言代码, 可选]
```

#### 语音聊天
```http
POST /api/v1/voice/chat
Content-Type: multipart/form-data

audio_file: [音频文件]
user_id: [用户ID]
gender: [性别: male/female/neutral]
```

#### 健康检查
```http
GET /api/v1/voice/health
```

### 支持的音频格式
- **音频格式**: MP3, WAV, M4A, FLAC, OGG, AAC
- **视频格式**: MP4, WebM (仅音轨)
- **最大文件大小**: 50MB
- **推荐格式**: WAV (最佳兼容性)

## 📚 文档

- [语音功能安装指南](docs/voice_to_text/INSTALLATION.md)
- [后端实现详解](docs/voice_to_text/backend_implementation.md)
- [前端集成指南](docs/voice_to_text/frontend_integration.md)
- [API 接口文档](docs/api_summary.md)

## 🧪 测试

### 运行测试脚本
```bash
# 语音功能测试
python test_voice_to_text.py

# API 测试
python tests/test_api.py
```

### 健康检查
```bash
curl https://your-server:8000/api/v1/voice/health
```

## 🔧 配置选项

### 环境变量
```bash
# Whisper 模型配置
WHISPER_MODEL_SIZE=base      # tiny, base, small, medium, large
WHISPER_DEVICE=cpu           # cpu 或 cuda

# 音频处理配置
MAX_AUDIO_FILE_SIZE=52428800 # 50MB
SUPPORTED_AUDIO_FORMATS=mp3,wav,m4a,flac,ogg,aac,mp4,webm

# AI 服务配置
CURRENT_AI_SERVICE=gemini    # gemini 或 kimi
```

## 🚀 部署

### Docker 部署
```bash
# 构建镜像
docker build -t wechat-demo-backend .

# 运行容器
docker run -p 8000:8000 wechat-demo-backend
```

### 生产环境
- 使用 Nginx 作为反向代理
- 配置 SSL 证书 (HTTPS 必需)
- 设置环境变量
- 配置日志轮转

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目采用 MIT 许可证。

## 📞 支持

如有问题，请查看：
1. [安装指南](docs/voice_to_text/INSTALLATION.md)
2. [故障排除](docs/voice_to_text/INSTALLATION.md#故障排除)
3. [Issue 列表](https://github.com/your-repo/issues)

---

**最后更新**: 2025年8月19日
**版本**: v0.1.0
