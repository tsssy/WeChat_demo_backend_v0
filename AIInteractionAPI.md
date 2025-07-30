# AIInteractionAPI 类设计文档

## 类说明
AI交互API类，负责处理与豆包API的直接交互，包括发送消息、获取响应和错误处理。

## 类定义
```python
class AIInteractionAPI:
    """AI交互API类"""
```

## 方法列表

### 1. send_message_to_ai (发送消息给AI)
```python
async def send_message_to_ai(self, user_id: int, message: str, history: list) -> dict
```
**功能说明：** 向豆包API发送消息并获取响应，包含内部重试机制

**请求体：**
```python
{
    "user_id": int,      # 用户ID
    "message": str,      # 当前用户消息
    "history": [         # 历史消息列表
        {
            "role": int,      # 0表示用户，1表示AI
            "content": str,   # 消息内容
            "timestamp": str  # ISO格式时间戳
        },
        ...
    ]
}
```

**豆包API请求体：**
```python
{
    "messages": [
        {
            "role": str,     # "user" 或 "assistant"（根据role字段转换）
            "content": str   # 消息内容
        }
    ],
    "temperature": float,   # 温度参数，控制随机性
    "top_p": float,        # 采样参数
    "max_tokens": int      # 最大生成token数
}
```

**回复体：**
```python
{
    "response": str,     # AI回复内容
    "status": str,      # "continue" 或 "end" 或 "error"
    "error": str,       # 如果失败，错误信息
    "metadata": {       # 元数据
        "tokens_used": int,    # 使用的token数
        "processing_time": float,  # 处理时间
        "model": str           # 使用的模型名称
    }
}
```

### 2. get_fallback_response (获取备用响应)
```python
async def get_fallback_response(self) -> dict
```
**功能说明：** 获取备用响应，在重试失败后使用

**回复体：**
```python
{
    "response": str,     # 预设的备用回复
    "status": "error",
    "error": str,       # 错误说明
    "metadata": {
        "fallback_type": str,  # 备用响应类型
        "original_error": str  # 原始错误信息
    }
}
```

### 3. handle_timeout_retry (处理超时重试)
```python
async def handle_timeout_retry(self, user_id: int, message: str) -> dict
```
**功能说明：** 处理超时重试逻辑

**请求体：**
```python
{
    "user_id": int,     # 用户ID
    "message": str,     # 原始消息
    "retry_count": int, # 当前重试次数
    "last_error": str   # 上次错误信息
}
```

**回复体：**
- 与send_message_to_ai相同的返回格式

## 错误码说明
```python
ERROR_CODES = {
    "TIMEOUT": {
        "code": "E001",
        "message": "请求超时"
    },
    "API_ERROR": {
        "code": "E002",
        "message": "API调用失败"
    },
    "RATE_LIMIT": {
        "code": "E003",
        "message": "超出调用频率限制"
    },
    "INVALID_RESPONSE": {
        "code": "E004",
        "message": "无效的响应格式"
    },
    "TOKEN_ERROR": {
        "code": "E005",
        "message": "Token验证失败"
    }
}
```

## 使用示例
```python
# 创建实例
ai_api = AIInteractionAPI()

# 发送消息
response = await ai_api.send_message_to_ai(
    user_id=123,
    message="你好",
    history=[]
)

# 处理响应
if response["status"] == "continue":
    print(response["response"])
elif response["status"] == "end":
    print(response["response"])
    # 处理总结
else:
    fallback = await ai_api.get_fallback_response()
    print(fallback["response"])
```

## 错误处理
1. API调用错误
   - 网络连接失败
   - 认证失败
   - 请求超时

2. 响应处理错误
   - 响应格式错误
   - 内容违规
   - JSON解析错误

3. 重试策略
   - 网络错误自动重试
   - 超时自动重试
   - 达到最大重试次数后返回备用响应

## 注意事项
1. 所有方法都是异步的，需要使用await调用
2. 内置了完善的重试机制
3. 统一的错误处理和返回格式
4. 注意API调用频率限制 
5. role字段使用整数（0表示用户，1表示AI） 