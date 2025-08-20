#!/bin/bash

# 语音转文字功能依赖安装脚本
# 适用于 macOS 和 Linux 系统

set -e

echo "🎤 开始安装语音转文字功能依赖..."

# 检查操作系统
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
else
    echo "❌ 不支持的操作系统: $OSTYPE"
    exit 1
fi

echo "✅ 检测到操作系统: $OS"

# 检查 conda 是否可用
if command -v conda &> /dev/null; then
    echo "✅ 检测到 conda"
    USE_CONDA=true
elif command -v brew &> /dev/null && [[ "$OS" == "macos" ]]; then
    echo "✅ 检测到 Homebrew"
    USE_CONDA=false
else
    echo "❌ 未检测到 conda 或 Homebrew，请先安装其中之一"
    exit 1
fi

# 安装 ffmpeg
echo "📦 安装 ffmpeg..."
if [[ "$USE_CONDA" == true ]]; then
    conda install -y -c conda-forge ffmpeg
else
    if [[ "$OS" == "macos" ]]; then
        brew install ffmpeg
    elif [[ "$OS" == "linux" ]]; then
        if command -v apt &> /dev/null; then
            sudo apt update && sudo apt install -y ffmpeg
        elif command -v yum &> /dev/null; then
            sudo yum install -y epel-release
            sudo yum install -y ffmpeg
        else
            echo "❌ 不支持的包管理器，请手动安装 ffmpeg"
            exit 1
        fi
    fi
fi

# 验证 ffmpeg 安装
if command -v ffmpeg &> /dev/null && command -v ffprobe &> /dev/null; then
    echo "✅ ffmpeg 安装成功"
    ffmpeg -version | head -n 1
else
    echo "❌ ffmpeg 安装失败"
    exit 1
fi

# 检查 Python 虚拟环境
if [[ -z "$VIRTUAL_ENV" ]] && [[ -z "$CONDA_DEFAULT_ENV" ]]; then
    echo "⚠️  警告: 未检测到激活的虚拟环境"
    echo "建议在虚拟环境中运行此脚本"
    read -p "是否继续? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 安装 Python 依赖
echo "🐍 安装 Python 依赖..."
pip install openai-whisper pydub python-multipart

# 验证 Python 包安装
echo "🔍 验证安装..."
python -c "
try:
    import whisper
    import pydub
    print('✅ 所有 Python 依赖安装成功!')
except ImportError as e:
    print(f'❌ Python 依赖安装失败: {e}')
    exit(1)
"

echo ""
echo "🎉 语音转文字功能依赖安装完成!"
echo ""
echo "📋 下一步操作:"
echo "1. 重启后端服务"
echo "2. 访问健康检查接口: GET /api/v1/voice/health"
echo "3. 测试语音功能"
echo ""
echo "📚 详细文档请查看: docs/voice_to_text/INSTALLATION.md"
