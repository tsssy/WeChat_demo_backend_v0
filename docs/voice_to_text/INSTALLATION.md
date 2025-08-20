# 语音转文字功能安装指南

## 系统要求

### 操作系统
- macOS 10.15+ (推荐)
- Linux (Ubuntu 18.04+, CentOS 7+)
- Windows 10+ (需要额外配置)

### Python环境
- Python 3.8+
- 推荐使用 conda 或 virtualenv 创建虚拟环境

## 安装步骤

### 1. 创建并激活虚拟环境

#### 使用 Conda (推荐)
```bash
# 创建环境
conda create -n miracle_backend_env python=3.11

# 激活环境
conda activate miracle_backend_env
```

#### 使用 Virtualenv
```bash
# 创建环境
python -m venv miracle_backend_env

# 激活环境 (macOS/Linux)
source miracle_backend_env/bin/activate

# 激活环境 (Windows)
miracle_backend_env\Scripts\activate
```

### 2. 安装系统依赖

#### macOS
```bash
# 使用 Homebrew 安装 ffmpeg
brew install ffmpeg

# 或者使用 Conda 安装 (推荐)
conda install -c conda-forge ffmpeg
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install ffmpeg
```

#### CentOS/RHEL
```bash
# 启用 EPEL 仓库
sudo yum install epel-release

# 安装 ffmpeg
sudo yum install ffmpeg
```

#### Windows
1. 下载 ffmpeg: https://ffmpeg.org/download.html
2. 解压到 `C:\ffmpeg`
3. 将 `C:\ffmpeg\bin` 添加到系统 PATH

### 3. 安装 Python 依赖

```bash
# 确保在虚拟环境中
pip install -r requirements.txt
```

### 4. 验证安装

```bash
# 检查 ffmpeg
ffmpeg -version

# 检查 ffprobe
ffprobe -version

# 检查 Python 包
python -c "import whisper; import pydub; print('所有依赖安装成功！')"
```

## 环境变量配置

在 `.env` 文件中添加以下配置：

```bash
# Whisper 模型配置
WHISPER_MODEL_SIZE=base  # tiny, base, small, medium, large
WHISPER_DEVICE=cpu       # cpu 或 cuda (如果有GPU)

# 音频文件配置
MAX_AUDIO_FILE_SIZE=52428800  # 50MB
SUPPORTED_AUDIO_FORMATS=mp3,wav,m4a,flac,ogg,aac,mp4,webm

# AI服务配置
CURRENT_AI_SERVICE=gemini  # gemini 或 kimi
```

## 模型下载

首次运行时，Whisper 会自动下载模型文件：

- **tiny**: ~39 MB
- **base**: ~74 MB  
- **small**: ~244 MB
- **medium**: ~769 MB
- **large**: ~1550 MB

模型文件会下载到用户目录的 `.cache/whisper/` 文件夹中。

## 故障排除

### 常见问题

#### 1. ffmpeg 未找到
```bash
# 错误信息
RuntimeWarning: Couldn't find ffprobe or avprobe

# 解决方案
conda install -c conda-forge ffmpeg
# 或
brew install ffmpeg
```

#### 2. 音频格式不支持
```bash
# 错误信息
不支持的音频格式: .xxx

# 解决方案
# 在 .env 中添加支持的格式
SUPPORTED_AUDIO_FORMATS=mp3,wav,m4a,flac,ogg,aac,mp4,webm
```

#### 3. 内存不足
```bash
# 错误信息
CUDA out of memory

# 解决方案
# 使用较小的模型或切换到 CPU
WHISPER_MODEL_SIZE=base
WHISPER_DEVICE=cpu
```

#### 4. 权限问题
```bash
# 错误信息
Permission denied

# 解决方案
# 确保有临时目录的写入权限
chmod 755 /tmp
```

## 性能优化

### CPU 优化
- 使用较小的模型 (tiny/base)
- 限制并发请求数量
- 使用音频预处理减少文件大小

### GPU 优化 (可选)
```bash
# 安装 CUDA 版本的 PyTorch
conda install pytorch torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia

# 设置环境变量
WHISPER_DEVICE=cuda
```

## 测试

安装完成后，可以运行测试脚本验证功能：

```bash
python test_voice_to_text.py
```

或者访问健康检查接口：

```bash
curl https://your-server:8000/api/v1/voice/health
```

## 更新依赖

```bash
# 更新 Python 包
pip install --upgrade -r requirements.txt

# 更新系统依赖
conda update ffmpeg
# 或
brew upgrade ffmpeg
```

## 支持的联系方式

如果遇到安装问题，请检查：
1. 虚拟环境是否正确激活
2. 系统依赖是否安装
3. Python 包版本兼容性
4. 环境变量配置
