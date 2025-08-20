# 项目目录结构说明

## 🏗️ 整体架构

```
WeChat_demo_backend_v0/
├── 📁 app/                      # 核心应用代码
├── 📁 docs/                     # 项目文档
├── 📁 tests/                    # 测试文件和脚本
├── 📁 config/                   # 配置文件
├── 📁 scripts/                  # 工具脚本
├── 📁 logs/                     # 日志文件
├── 📁 telegram_bot/             # Telegram机器人
├── 📄 requirements.txt           # Python依赖
├── 📄 README.md                 # 项目说明
└── 📄 PROJECT_STRUCTURE.md      # 本文件
```

## 📁 目录详细说明

### 1. 核心应用 (`app/`)
```
app/
├── 📁 api/                      # API接口层
│   └── 📁 v1/                  # API版本1
│       ├── UserManagement.py    # 用户管理API
│       ├── MatchManager.py      # 匹配管理API
│       ├── ChatroomManager.py   # 聊天室管理API
│       ├── AIResponseProcessor.py # AI响应处理API
│       ├── PersonalityTest.py   # 个性测试API
│       └── VoiceToText.py      # 语音转文字API
├── 📁 core/                     # 核心模块
│   ├── database.py              # 数据库连接
│   └── security.py              # 安全相关
├── 📁 objects/                  # 数据模型
│   ├── User.py                  # 用户模型
│   ├── Match.py                 # 匹配模型
│   ├── Chatroom.py              # 聊天室模型
│   ├── Message.py               # 消息模型
│   ├── PersonalityCard.py       # 个性卡片模型
│   ├── PersonalityQuestion.py   # 个性问题模型
│   └── PersonalityTestRecord.py # 个性测试记录模型
├── 📁 schemas/                  # 数据验证模式
│   ├── UserManagement.py        # 用户管理模式
│   ├── MatchManager.py          # 匹配管理模式
│   ├── ChatroomManager.py       # 聊天室管理模式
│   ├── AIResponseProcessor.py   # AI响应处理模式
│   ├── PersonalityTest.py       # 个性测试模式
│   └── VoiceToText.py          # 语音转文字模式
├── 📁 services/                 # 业务逻辑层
│   └── 📁 https/               # HTTP服务
│       ├── UserManagement.py    # 用户管理服务
│       ├── MatchManager.py      # 匹配管理服务
│       ├── ChatroomManager.py   # 聊天室管理服务
│       ├── AIResponseProcessor.py # AI响应处理服务
│       ├── PersonalityTestManager.py # 个性测试管理服务
│       ├── VoiceToTextService.py # 语音转文字服务
│       ├── GeminiInteractionAPI.py # Gemini AI交互
│       ├── KimiInteractionAPI.py # Kimi AI交互
│       ├── N8nWebhookManager.py # N8N Webhook管理
│       └── DataIntegrity.py     # 数据完整性检查
├── 📁 utils/                    # 工具模块
│   ├── my_logger.py             # 日志工具
│   ├── prompt_manager.py        # 提示词管理
│   ├── singleton_status.py      # 单例状态管理
│   ├── ssl_helper.py            # SSL助手
│   └── audio_processor.py       # 音频处理工具
├── 📁 prompts/                  # AI提示词
│   ├── role.md                  # 角色定义
│   ├── object.md                # 目标定义
│   ├── skill.md                 # 技能定义
│   ├── constraint.md            # 约束定义
│   ├── workflow.md              # 工作流程
│   ├── male.md                  # 男性特定提示词
│   ├── female.md                # 女性特定提示词
│   └── neutral.md               # 中性提示词
├── 📁 WebSocketsService/        # WebSocket服务
│   ├── ConnectionHandler.py     # 连接处理
│   ├── MatchSessionHandler.py   # 匹配会话处理
│   └── MessageConnectionHandler.py # 消息连接处理
├── 📁 ws/                       # WebSocket路由
│   ├── base.py                  # 基础WebSocket
│   ├── match.py                 # 匹配WebSocket
│   └── message.py               # 消息WebSocket
├── config.py                    # 应用配置
└── server_run.py                # 服务器启动文件
```

### 2. 文档目录 (`docs/`)
```
docs/
├── 📁 voice_to_text/            # 语音转文字功能文档
│   ├── README.md                # 功能概述
│   ├── INSTALLATION.md          # 安装指南
│   ├── backend_implementation.md # 后端实现详解
│   ├── frontend_integration.md  # 前端集成指南
│   └── DEPENDENCIES.md          # 依赖分析
├── 📁 nginx_tutorial/           # Nginx教程
├── 📁 clash_config/             # 代理配置
├── api_summary.md                # API接口总结
├── CORS_CONFIG.md                # CORS配置说明
├── frontend_deployment_guide.md  # 前端部署指南
├── FRONTEND_INTEGRATION_GUIDE.md # 前端集成指南
├── MODIFICATION_LOG.md           # 修改日志
├── QUICK_RESTORE.md             # 快速恢复指南
├── AI_Interface_Documentation.md # AI接口文档
├── AIInteractionAPI.md          # AI交互API文档
├── AI_API_Documentation.md      # AI API文档
├── AIResponseProcessor.md       # AI响应处理器文档
└── 抽卡游戏前端调用指南.md       # 抽卡游戏指南
```

### 3. 测试目录 (`tests/`)
```
tests/
├── 📁 unit/                     # 单元测试
│   ├── test_voice_to_text.py    # 语音功能测试
│   ├── test_memory_personality.py # 记忆个性测试
│   ├── test_personality_api.py  # 个性API测试
│   ├── test_card_game_complete.py # 抽卡游戏测试
│   ├── test_kimi_complete.py    # Kimi AI测试
│   ├── test_api.py              # API基础测试
│   ├── test_auth_fix.py         # 认证修复测试
│   ├── test_chatroom.py         # 聊天室测试
│   ├── test_n8n_simple.py      # N8N简单测试
│   ├── test_n8n_singleton.py   # N8N单例测试
│   └── test_n8n_webhook_manager.py # N8N Webhook测试
├── 📁 integration/              # 集成测试
│   ├── test_comprehensive_deactivate.py # 综合停用测试
│   ├── test_deactivate_direct.py # 直接停用测试
│   ├── test_deactivate_user.py  # 用户停用测试
│   └── test_user_deletion_with_chatrooms.py # 用户删除测试
├── 📁 e2e/                      # 端到端测试
│   ├── test_step1_setup_environment.py # 环境设置测试
│   ├── test_get_new_matches_for_everyone.py # 匹配系统测试
│   └── run_database_integrity_check.py # 数据库完整性检查
├── 📁 frontend/                 # 前端测试
│   ├── websocket_test_suite.html # WebSocket测试套件
│   ├── private_chat_test.html   # 私聊测试
│   ├── match_session_test.html  # 匹配会话测试
│   ├── test.html                # 基础测试页面
│   ├── frontend_base_test.js    # 基础前端测试
│   ├── frontend_match_test.js   # 匹配前端测试
│   └── frontend_message_test.js # 消息前端测试
├── 📁 scripts/                  # 测试脚本
│   ├── create_test_users.py     # 创建测试用户
│   ├── create_complete_test_env.py # 创建完整测试环境
│   ├── generate_fake_data.py    # 生成假数据
│   ├── generate_fake_users.py   # 生成假用户
│   ├── check_user_cache.py      # 检查用户缓存
│   ├── query_matches.py         # 查询匹配
│   ├── verify_match_ids.py      # 验证匹配ID
│   └── fix_match_ids.py         # 修复匹配ID
├── README.md                     # 测试说明
└── api_test_example.md           # API测试示例
```

### 4. 配置目录 (`config/`)
```
config/
├── README.md                     # 配置说明
├── nginx_config_new.conf         # Nginx配置文件
├── requirements_pip.txt          # pip依赖列表
└── requirements_conda.txt        # conda依赖列表
```

### 5. 脚本目录 (`scripts/`)
```
scripts/
├── README.md                     # 脚本说明
└── install_voice_deps.sh         # 语音功能依赖安装脚本
```

### 6. 其他目录
```
logs/                             # 日志文件
telegram_bot/                     # Telegram机器人
├── main.py                       # 主程序
├── matchmaker_bot.py             # 匹配机器人
├── config.py                     # 机器人配置
├── README.md                     # 机器人说明
└── 📁 prompts/                   # 机器人提示词
```

## 🔄 文件移动历史

### 测试文件整理
- ✅ 单元测试 → `tests/unit/`
- ✅ 集成测试 → `tests/integration/`
- ✅ 端到端测试 → `tests/e2e/`
- ✅ 前端测试 → `tests/frontend/`
- ✅ 测试脚本 → `tests/scripts/`

### 配置文件整理
- ✅ Nginx配置 → `config/`
- ✅ 依赖列表 → `config/`
- ✅ 安装脚本 → `scripts/`

### 文档文件整理
- ✅ AI相关文档 → `docs/`
- ✅ 游戏指南 → `docs/`

## 📋 目录命名规范

### 1. 目录命名
- 使用小写字母和下划线
- 名称要清晰表达用途
- 避免使用缩写和特殊字符

### 2. 文件命名
- Python文件: 小写字母和下划线
- 测试文件: `test_*.py`
- 配置文件: `*_config.*`
- 文档文件: 描述性名称

### 3. 分类原则
- **功能相关**: 按功能模块分组
- **类型相关**: 按文件类型分组
- **用途相关**: 按使用目的分组

## 🚀 使用建议

### 1. 开发工作流
```bash
# 1. 在相应目录下创建新功能
cd app/services/https/
# 创建新的服务文件

# 2. 在对应测试目录下编写测试
cd tests/unit/
# 创建对应的测试文件

# 3. 更新相关文档
cd docs/
# 更新功能文档
```

### 2. 文件查找
```bash
# 查找特定功能的文件
find . -name "*voice*" -type f

# 查找测试文件
find tests/ -name "test_*.py"

# 查找配置文件
find config/ -name "*.conf"
```

### 3. 代码组织
- 新功能放在对应的功能目录下
- 测试文件放在对应的测试目录下
- 配置放在config目录下
- 工具脚本放在scripts目录下

## 📚 相关文档

- [项目README](README.md)
- [测试说明](tests/README.md)
- [配置说明](config/README.md)
- [脚本说明](scripts/README.md)
- [语音功能文档](docs/voice_to_text/README.md)

---

**最后更新**: 2025年8月19日
**维护者**: 开发团队
