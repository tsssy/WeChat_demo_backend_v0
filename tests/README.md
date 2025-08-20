# 测试目录说明

## 📁 目录结构

```
tests/
├── README.md                    # 本文件
├── unit/                        # 单元测试
│   ├── test_voice_to_text.py   # 语音转文字功能测试
│   ├── test_memory_personality.py # 记忆和个性测试
│   ├── test_personality_api.py # 个性API测试
│   ├── test_card_game_complete.py # 抽卡游戏测试
│   ├── test_kimi_complete.py   # Kimi AI测试
│   ├── test_api.py             # API基础测试
│   ├── test_auth_fix.py        # 认证修复测试
│   ├── test_chatroom.py        # 聊天室测试
│   ├── test_n8n_simple.py     # N8N简单测试
│   ├── test_n8n_singleton.py  # N8N单例测试
│   └── test_n8n_webhook_manager.py # N8N Webhook管理测试
├── integration/                 # 集成测试
│   ├── test_comprehensive_deactivate.py # 综合停用测试
│   ├── test_deactivate_direct.py # 直接停用测试
│   ├── test_deactivate_user.py # 用户停用测试
│   └── test_user_deletion_with_chatrooms.py # 用户删除和聊天室测试
├── e2e/                        # 端到端测试
│   ├── test_step1_setup_environment.py # 环境设置测试
│   ├── test_get_new_matches_for_everyone.py # 匹配系统测试
│   └── run_database_integrity_check.py # 数据库完整性检查
├── frontend/                    # 前端测试
│   ├── websocket_test_suite.html # WebSocket测试套件
│   ├── private_chat_test.html   # 私聊测试
│   ├── match_session_test.html  # 匹配会话测试
│   ├── test.html                # 基础测试页面
│   ├── frontend_base_test.js    # 基础前端测试
│   ├── frontend_match_test.js   # 匹配前端测试
│   └── frontend_message_test.js # 消息前端测试
├── scripts/                     # 测试脚本
│   ├── create_test_users.py     # 创建测试用户
│   ├── create_complete_test_env.py # 创建完整测试环境
│   ├── generate_fake_data.py    # 生成假数据
│   ├── generate_fake_users.py   # 生成假用户
│   ├── check_user_cache.py      # 检查用户缓存
│   ├── query_matches.py         # 查询匹配
│   ├── verify_match_ids.py      # 验证匹配ID
│   └── fix_match_ids.py         # 修复匹配ID
└── api_test_example.md          # API测试示例文档
```

## 🧪 测试类型说明

### 1. 单元测试 (Unit Tests)
- **位置**: `tests/unit/`
- **目的**: 测试单个函数、类或模块的功能
- **特点**: 快速、独立、可重复
- **运行方式**: `python -m pytest tests/unit/`

### 2. 集成测试 (Integration Tests)
- **位置**: `tests/integration/`
- **目的**: 测试多个组件之间的交互
- **特点**: 中等速度、测试组件协作
- **运行方式**: `python -m pytest tests/integration/`

### 3. 端到端测试 (E2E Tests)
- **位置**: `tests/e2e/`
- **目的**: 测试完整的业务流程
- **特点**: 较慢、测试真实场景
- **运行方式**: `python -m pytest tests/e2e/`

### 4. 前端测试 (Frontend Tests)
- **位置**: `tests/frontend/`
- **目的**: 测试前端界面和交互
- **特点**: 浏览器环境、UI测试
- **运行方式**: 在浏览器中打开HTML文件

### 5. 测试脚本 (Test Scripts)
- **位置**: `tests/scripts/`
- **目的**: 辅助测试的工具脚本
- **特点**: 数据准备、环境设置
- **运行方式**: `python tests/scripts/script_name.py`

## 🚀 运行测试

### 运行所有测试
```bash
# 使用pytest运行所有测试
python -m pytest tests/

# 运行特定类型的测试
python -m pytest tests/unit/      # 单元测试
python -m pytest tests/integration/ # 集成测试
python -m pytest tests/e2e/       # 端到端测试
```

### 运行特定测试文件
```bash
# 运行语音功能测试
python -m pytest tests/unit/test_voice_to_text.py

# 运行认证测试
python -m pytest tests/unit/test_auth_fix.py
```

### 运行前端测试
```bash
# 在浏览器中打开测试页面
open tests/frontend/websocket_test_suite.html
open tests/frontend/private_chat_test.html
```

## 📋 测试环境要求

### 1. Python环境
- Python 3.8+
- 虚拟环境 (推荐: `miracle_backend_env`)

### 2. 依赖包
```bash
# 安装测试依赖
pip install pytest pytest-asyncio pytest-cov

# 安装项目依赖
pip install -r requirements.txt
```

### 3. 系统依赖
- MongoDB 运行中
- ffmpeg (语音测试需要)

### 4. 环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 配置测试环境
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=test_db
```

## 🔧 测试配置

### 1. pytest配置
创建 `pytest.ini` 文件：
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

### 2. 测试数据
- 测试数据存储在 `tests/data/` 目录
- 使用 `tests/scripts/` 中的脚本生成测试数据

## 📊 测试覆盖率

### 生成覆盖率报告
```bash
# 运行测试并生成覆盖率报告
python -m pytest --cov=app tests/

# 生成HTML报告
python -m pytest --cov=app --cov-report=html tests/
```

### 查看覆盖率报告
```bash
# 打开HTML报告
open htmlcov/index.html
```

## 🐛 故障排除

### 常见问题

#### 1. 数据库连接失败
```bash
# 检查MongoDB状态
sudo systemctl status mongod

# 启动MongoDB
sudo systemctl start mongod
```

#### 2. 依赖包缺失
```bash
# 激活虚拟环境
conda activate miracle_backend_env

# 安装依赖
pip install -r requirements.txt
```

#### 3. 权限问题
```bash
# 检查文件权限
ls -la tests/

# 修复权限
chmod +x tests/scripts/*.py
```

## 📝 添加新测试

### 1. 创建测试文件
```python
# tests/unit/test_new_feature.py
import pytest
from app.services.new_feature import NewFeature

class TestNewFeature:
    def test_basic_functionality(self):
        feature = NewFeature()
        assert feature.doSomething() == "expected_result"
```

### 2. 遵循命名规范
- 测试文件: `test_*.py`
- 测试类: `Test*`
- 测试方法: `test_*`

### 3. 使用适当的测试类型
- 简单功能 → 单元测试
- 组件交互 → 集成测试
- 完整流程 → 端到端测试

## 🤝 贡献指南

1. **编写测试**: 为新功能编写相应的测试
2. **维护测试**: 及时更新过时的测试
3. **测试覆盖**: 确保关键功能有足够的测试覆盖
4. **文档更新**: 更新测试说明和示例

---

**最后更新**: 2025年8月19日
**维护者**: 开发团队
