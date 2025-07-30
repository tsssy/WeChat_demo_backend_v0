# 前端请求的AI聊天接口文档

## 接口概述
本文档描述了AI聊天功能的前端接口。前端需要调用两个主要接口：获取历史记录和发送/接收消息。

## 1. 获取聊天历史
### 接口说明
获取指定用户的AI聊天历史记录。如果是首次对话，返回空列表。

### 接口信息
- **路由**: POST /api/v1/ai/history
- **方法**: POST
- **接口名称**: get_ai_chat_history

### 请求体
```python
{
    "user_id": int     # 用户ID
}
```

### 返回格式
```python
{
    "status": "success",
    "data": [
        (
            str,   # message_content: 消息内容
            str,   # message_send_time_in_utc: ISO格式的时间字符串
            int,   # message_sender_id: 发送者ID
            str    # display_name: 显示名称（根据role显示"I"或"AI Assistant"）
        ),
        ...
    ]
}
```

### 示例
```json
{
    "status": "success",
    "data": [
        [
            "你好，我是AI助手",
            "2024-03-21T10:00:00Z",
            0,
            "AI Assistant"
        ],
        [
            "你好",
            "2024-03-21T10:01:00Z",
            123,
            "I"
        ]
    ]
}
```

## 2. 发送消息接口
### 接口说明
发送消息给AI并获取回复。包括首次对话（空消息）和后续对话。

### 接口信息
- **路由**: POST /api/v1/ai/chat
- **方法**: POST
- **接口名称**: handle_ai_chat

### 请求体
```python
{
    "user_id": int,    # 用户ID
    "message": str     # 用户消息（首次对话可以为空字符串）
}
```

### 返回格式
```python
{
    "status": str,     # "continue" 或 "end" 或 "error"
    "response": str,   # AI的回复内容
    "summary": {       # 仅在status为"end"时存在
        "part1": str,  # 总结第一部分
        "part2": str   # 总结第二部分
    },
    "error": str      # 仅在status为"error"时存在
}
```

### 示例
1. 普通对话响应：
```json
{
    "status": "continue",
    "response": "很高兴认识你！请问有什么我可以帮助你的吗？"
}
```

2. 对话结束响应：
```json
{
    "status": "end",
    "response": "感谢你的分享...",
    "summary": {
        "part1": "根据我们的对话，以下是主要总结...",
        "part2": "这里是一些建议..."
    }
}
```

3. 错误响应：
```json
{
    "status": "error",
    "error": "服务暂时不可用，请稍后重试"
}
```

## 使用流程
1. 用户进入聊天页面：
   - 调用历史记录接口获取已有对话
   - 如果返回空列表，调用发送消息接口（空消息）获取AI首次回复

2. 用户发送消息：
   - 调用发送消息接口
   - 根据返回的status处理不同情况：
     - continue: 显示AI回复，继续对话
     - end: 显示总结，结束对话
     - error: 显示错误信息

## 注意事项
1. 所有时间戳使用ISO格式的UTC时间
2. 用户ID必须是整数
3. 消息内容不能为null（首次对话可以是空字符串）
4. 总结消息需要分两部分显示
5. 数据库表结构：
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