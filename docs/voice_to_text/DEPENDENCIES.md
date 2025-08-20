# 项目依赖分析文档

## 📦 核心依赖包

### 1. Web框架和服务器
- **fastapi** (>=0.104.0): 现代、快速的Web框架，用于构建API
- **uvicorn[standard]** (>=0.24.0): ASGI服务器，用于运行FastAPI应用

### 2. 环境配置
- **python-dotenv** (>=1.0.0): 从.env文件加载环境变量

### 3. 数据库
- **motor** (>=3.3.0): MongoDB的异步Python驱动
- **pymongo** (>=4.6.0): MongoDB的Python驱动

### 4. 数据验证
- **pydantic** (>=2.5.0): 数据验证和设置管理

### 5. 认证和安全
- **python-jose[cryptography]** (>=3.3.0): JWT令牌处理

### 6. HTTP客户端
- **aiohttp** (>=3.9.0): 异步HTTP客户端/服务器
- **httpx** (>=0.25.0): 现代化的HTTP客户端
- **requests** (>=2.31.0): HTTP库

## 🎤 语音转文字功能依赖

### 1. 核心语音识别
- **openai-whisper** (>=20231117): OpenAI的语音识别模型
  - 支持多种语言
  - 高精度转录
  - 支持多种音频格式

### 2. 音频处理
- **pydub** (>=0.25.1): 音频文件操作库
  - 格式转换
  - 音频信息提取
  - 依赖ffmpeg进行底层处理

### 3. 文件上传
- **python-multipart** (>=0.0.6): 处理multipart/form-data请求
  - 支持文件上传
  - 表单数据处理

## 🔧 系统依赖

### 1. 必需的系统工具
- **ffmpeg**: 音频/视频处理工具
  - 音频格式转换
  - 音频信息提取
  - 支持多种编解码器

### 2. 安装方式
```bash
# macOS (推荐)
conda install -c conda-forge ffmpeg

# 或使用Homebrew
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# CentOS/RHEL
sudo yum install epel-release
sudo yum install ffmpeg
```

## 📚 Python标准库依赖

以下模块是Python标准库的一部分，无需额外安装：

### 1. 核心模块
- **logging**: 日志记录
- **pathlib**: 路径操作
- **typing**: 类型提示
- **datetime**: 日期时间处理
- **json**: JSON数据处理
- **os**: 操作系统接口
- **sys**: 系统特定参数
- **tempfile**: 临时文件和目录
- **asyncio**: 异步I/O
- **ssl**: SSL/TLS包装器

### 2. 文件处理
- **urllib3**: HTTP客户端库
- **ssl**: SSL/TLS支持

## 🚀 可选依赖

### 1. GPU加速 (CUDA环境)
```bash
# 安装CUDA版本的PyTorch
conda install pytorch torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia

# 设置环境变量
export WHISPER_DEVICE=cuda
```

### 2. 性能优化
- **ujson** (>=5.8.0): 更快的JSON处理
- **orjson** (>=3.9.0): 最快的JSON处理库

### 3. 高级音频处理
- **librosa** (>=0.10.0): 音频和音乐分析
- **soundfile** (>=0.12.0): 音频文件读写

## 📋 依赖安装顺序

### 1. 系统依赖
```bash
# 首先安装ffmpeg
conda install -c conda-forge ffmpeg
```

### 2. Python包
```bash
# 安装核心依赖
pip install -r requirements.txt

# 或分步安装
pip install fastapi uvicorn[standard] python-dotenv
pip install motor pymongo pydantic
pip install python-jose[cryptography]
pip install aiohttp httpx requests
pip install openai-whisper pydub python-multipart
```

## 🔍 依赖检查

### 1. 验证安装
```bash
# 检查ffmpeg
ffmpeg -version
ffprobe -version

# 检查Python包
python -c "
import whisper
import pydub
import fastapi
import motor
print('✅ 所有依赖安装成功!')
"
```

### 2. 版本兼容性
```bash
# 检查包版本
pip list | grep -E "(fastapi|uvicorn|whisper|pydub)"
```

## ⚠️ 常见问题

### 1. ffmpeg未找到
```bash
# 错误信息
RuntimeWarning: Couldn't find ffprobe or avprobe

# 解决方案
conda install -c conda-forge ffmpeg
```

### 2. 音频格式不支持
```bash
# 确保ffmpeg支持所需格式
ffmpeg -formats | grep -E "(mp3|wav|m4a|flac|ogg|aac|mp4|webm)"
```

### 3. 内存不足
```bash
# 使用较小的Whisper模型
export WHISPER_MODEL_SIZE=tiny  # 或 base
```

## 📊 依赖关系图

```
项目根目录
├── 核心Web框架
│   ├── fastapi
│   └── uvicorn
├── 数据库层
│   ├── motor (异步)
│   └── pymongo (同步)
├── 语音处理
│   ├── openai-whisper
│   ├── pydub
│   └── ffmpeg (系统依赖)
├── 工具库
│   ├── pydantic
│   ├── python-dotenv
│   └── python-multipart
└── HTTP客户端
    ├── aiohttp
    ├── httpx
    └── requests
```

## 🔄 更新和维护

### 1. 定期更新
```bash
# 更新Python包
pip install --upgrade -r requirements.txt

# 更新系统依赖
conda update ffmpeg
```

### 2. 安全更新
```bash
# 检查安全漏洞
pip-audit

# 更新有安全问题的包
pip install --upgrade <package-name>
```

## 📝 注意事项

1. **ffmpeg版本**: 确保使用较新版本以支持所有音频格式
2. **Python版本**: 推荐使用Python 3.8+
3. **虚拟环境**: 始终在虚拟环境中安装依赖
4. **系统兼容性**: 某些依赖在不同操作系统上可能有差异
5. **网络环境**: 某些包的下载可能需要配置代理

---

**最后更新**: 2025年8月19日
**维护者**: 开发团队
