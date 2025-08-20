# 脚本目录说明

## 📁 目录结构

```
scripts/
├── README.md                    # 本文件
└── install_voice_deps.sh        # 语音功能依赖安装脚本
```

## 🛠️ 脚本说明

### 1. 语音功能依赖安装脚本
- **文件**: `install_voice_deps.sh`
- **用途**: 自动安装语音转文字功能所需的系统依赖和Python包
- **支持系统**: macOS, Linux
- **包管理器**: conda, Homebrew, apt, yum

## 🚀 使用方法

### 运行安装脚本
```bash
# 给脚本添加执行权限
chmod +x scripts/install_voice_deps.sh

# 运行脚本
./scripts/install_voice_deps.sh
```

### 手动安装依赖
```bash
# 激活虚拟环境
conda activate miracle_backend_env

# 安装ffmpeg
conda install -c conda-forge ffmpeg

# 安装Python包
pip install openai-whisper pydub python-multipart
```

## 📋 脚本功能

### 自动检测
- 操作系统类型 (macOS/Linux)
- 可用的包管理器 (conda/Homebrew/apt/yum)
- Python虚拟环境状态

### 依赖安装
- **系统依赖**: ffmpeg (音频处理)
- **Python包**: whisper, pydub, python-multipart
- **验证**: 检查安装是否成功

### 环境配置
- 检查虚拟环境
- 验证依赖版本
- 提供后续操作指导

## 🔧 脚本参数

### 环境变量
```bash
# 设置Whisper模型大小
export WHISPER_MODEL_SIZE=base

# 设置设备类型
export WHISPER_DEVICE=cpu

# 设置音频文件大小限制
export MAX_AUDIO_FILE_SIZE=52428800
```

### 命令行选项
```bash
# 静默安装 (非交互式)
./install_voice_deps.sh --silent

# 指定Python版本
./install_voice_deps.sh --python-version 3.11

# 跳过系统依赖检查
./install_voice_deps.sh --skip-system-deps
```

## 📊 安装流程

### 1. 环境检查
```bash
# 检查操作系统
# 检查包管理器
# 检查Python环境
# 检查虚拟环境
```

### 2. 系统依赖安装
```bash
# 安装ffmpeg
# 验证安装
# 检查版本
```

### 3. Python包安装
```bash
# 安装核心包
# 安装语音包
# 验证导入
```

### 4. 配置验证
```bash
# 检查配置
# 运行测试
# 生成报告
```

## 🐛 故障排除

### 常见问题

#### 1. 权限不足
```bash
# 错误信息
Permission denied

# 解决方案
sudo chmod +x scripts/install_voice_deps.sh
```

#### 2. 包管理器未找到
```bash
# 错误信息
conda: command not found

# 解决方案
# 安装conda或使用其他包管理器
```

#### 3. 网络问题
```bash
# 错误信息
Connection timeout

# 解决方案
# 配置代理或使用镜像源
```

### 调试模式
```bash
# 启用调试输出
bash -x scripts/install_voice_deps.sh

# 或设置环境变量
export DEBUG=1
./scripts/install_voice_deps.sh
```

## 📝 自定义脚本

### 创建新的安装脚本
```bash
#!/bin/bash
# 自定义安装脚本示例

set -e

echo "开始安装自定义功能..."

# 安装依赖
pip install custom_package

# 配置环境
echo "export CUSTOM_VAR=value" >> ~/.bashrc

echo "安装完成!"
```

### 脚本模板
```bash
#!/bin/bash
# 脚本名称: script_name.sh
# 用途: 描述脚本功能
# 作者: 作者姓名
# 日期: 创建日期

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 主函数
main() {
    log_info "开始执行脚本..."
    
    # 脚本逻辑
    
    log_info "脚本执行完成!"
}

# 执行主函数
main "$@"
```

## 🔄 维护和更新

### 定期检查
```bash
# 检查脚本权限
ls -la scripts/

# 验证脚本功能
./scripts/install_voice_deps.sh --test

# 更新依赖版本
pip list --outdated
```

### 版本管理
```bash
# 创建版本标签
git tag -a v1.0.0 -m "Release version 1.0.0"

# 推送标签
git push origin v1.0.0
```

## 📚 相关文档

- [Bash脚本编写指南](https://tldp.org/LDP/abs/html/)
- [conda包管理](https://docs.conda.io/)
- [pip包管理](https://pip.pypa.io/en/stable/)

---

**最后更新**: 2025年8月19日
**维护者**: 开发团队
