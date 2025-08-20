# AIResponseProcessor 类设计文档

## 类说明
AI响应处理器类，负责处理豆包API响应的存储、分析和管理。

## 类定义
```python
class AIResponseProcessor:
    """AI响应处理器类"""
```

## 方法列表

### 1. save_conversation_history (保存对话历史)
```python
async def save_conversation_history(self, user_id: int, message: str, response: str) -> bool
```
**功能说明：** 保存对话历史记录

**请求体：**
```python
{
    "user_id": int,     # 用户ID
    "message": {
        "content": str,   # 用户消息内容
        "role": int,      # 0表示用户
        "timestamp": str  # ISO格式时间戳
    },
    "response": {
        "content": str,   # AI响应内容
        "role": int,      # 1表示AI
        "timestamp": str  # ISO格式时间戳
    }
}
```

**回复体：**
```python
{
    "success": bool,      # 是否保存成功
    "message": str,       # 成功或错误信息
    "data": {
        "message_id": int,  # 消息ID
        "timestamp": str    # 保存时间
    }
}
```

### 2. get_conversation_history (获取对话历史)
```python
async def get_conversation_history(self, user_id: int) -> list
```
**功能说明：** 获取对话历史记录

**请求体：**
```python
{
    "user_id": int     # 用户ID
}
```

**回复体：**
```python
[
    (
        str,   # message_content: 消息内容
        str,   # message_send_time_in_utc: ISO格式时间字符串
        int,   # message_sender_id: 发送者ID
        str    # display_name: 显示名称（根据role显示"I"或"AI Assistant"）
    ),
    ...
]
```

### 3. check_conversation_end (检查对话结束)
```python
async def check_conversation_end(self, response: str) -> bool
```
**功能说明：** 检查对话是否结束

**请求体：**
```python
{
    "response": str,          # AI响应内容
    "conversation_stats": {
        "total_rounds": int,  # 当前对话轮数
        "duration": int,      # 对话持续时间（秒）
        "last_active": str    # 最后活动时间
    }
}
```

**回复体：**
```python
{
    "should_end": bool,      # 是否应该结束对话
    "reason": str,          # 结束原因（如果should_end为true）
    "metadata": {
        "rounds": int,      # 当前轮数
        "max_rounds": int,  # 最大轮数
        "duration": int     # 持续时间
    }
}
```

### 4. process_final_summary (处理最终总结)
```python
async def process_final_summary(self, response: str) -> dict
```
**功能说明：** 处理最终总结

**请求体：**
```python
{
    "response": str,         # AI的最终响应
    "user_id": int,         # 用户ID
    "conversation_data": {
        "total_messages": int,  # 总消息数
        "duration": int,        # 对话持续时间
        "start_time": str       # 开始时间
    }
}
```

**回复体：**
```python
{
    "status": "end",
    "summary": {
        "part1": str,  # 总结第一部分
        "part2": str   # 总结第二部分
    }
}
```

## 数据库结构
```python
# AI_chatroom 表
{
    "user_id": int,              # 用户ID
    "ai_message_ids": [int]     # 消息ID列表
}

# AI_message 表
{
    "ai_message_id": int,                    # 消息ID
    "ai_message_content": str,               # 消息内容
    "ai_message_send_time_in_utc": datetime, # 发送时间
    "role": int                              # 0表示用户，1表示AI
}
```

## 使用示例
```python
# 创建实例
processor = AIResponseProcessor()

# 保存对话
success = await processor.save_conversation_history(
    user_id=123,
    message="用户消息",
    response="AI回复"
)

# 获取历史
history = await processor.get_conversation_history(user_id=123)

# 检查是否结束
is_end = await processor.check_conversation_end(response="AI回复内容")

# 处理最终总结
if is_end["should_end"]:
    summary = await processor.process_final_summary(response="最终回复")
```

## 注意事项
1. 数据持久化需要考虑并发安全
2. 注意内存使用，特别是长对话场景
3. 定期清理过期的历史记录
4. 确保响应处理的稳定性和可靠性
5. role字段使用整数（0表示用户，1表示AI）
6. 所有ID字段使用整数类型 