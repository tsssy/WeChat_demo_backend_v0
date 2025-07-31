# AI聊天接口文档

## 概述

本文档详细说明了AI聊天功能的前端调用方式，包括接口格式、功能说明、返回情况和数据库格式。主要包含两个核心接口：获取聊天历史和发送AI聊天消息。

**重要说明**: 本文档中的所有数据格式都与后端实际接口完全对应，确保前端开发时不会出现格式不匹配的问题。

---

## 接口列表

### 1. 获取AI聊天历史记录

#### 接口信息
- **URL**: `/api/v1/ai/history`
- **方法**: `POST`
- **Content-Type**: `application/json`
- **功能**: 获取指定用户的AI聊天历史记录

#### 请求格式

```json
{
  "user_id": 12345
}
```

#### 请求参数说明

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| user_id | integer | 是 | 用户ID，用于获取该用户的聊天历史 |

#### 返回格式

**成功情况**:
```json
{
  "status": "success",
  "data": [
    ["你好，我想了解一下你的服务", "2024-01-15T10:30:00.000Z", 12345, "I"],
    ["你好！很高兴为你服务。我是你的AI助手，可以帮你解答各种问题。请告诉我你需要什么帮助？", "2024-01-15T10:30:05.000Z", 999, "AI Assistant"]
  ],
  "error": null
}
```

**失败情况**:
```json
{
  "status": "error",
  "data": [],
  "error": "获取聊天历史失败: 数据库连接异常"
}
```

#### 返回参数说明

| 参数名 | 类型 | 说明 |
|--------|------|------|
| status | string | 响应状态，"success" 或 "error" |
| data | array | 聊天记录数组，新用户为空数组 |
| error | string/null | 错误信息，成功时为null |

**注意**: 后端返回的data是元组数组格式，前端代码中会自动转换为对象数组格式以便使用。

**data数组中的消息元组说明**:

| 索引 | 类型 | 说明 |
|------|------|------|
| 0 | string | 消息内容 |
| 1 | string | ISO格式时间字符串 |
| 2 | integer | 发送者ID (用户ID或AI用户ID: 999) |
| 3 | string | 显示名称 ("I" 表示用户, "AI Assistant" 表示AI) |

#### 特殊情况说明

1. **新用户**: 首次使用AI聊天功能的用户，返回空数组
2. **老用户**: 有聊天历史的用户，返回按时间排序的完整历史记录
3. **网络异常**: 返回错误状态和具体错误信息

---

### 2. 发送AI聊天消息

#### 接口信息
- **URL**: `/api/v1/ai/chat`
- **方法**: `POST`
- **Content-Type**: `application/json`
- **功能**: 发送用户消息给AI，获取AI回复并保存对话记录

#### 请求格式

```json
{
  "user_id": 12345,
  "message": "我想了解一下你们的产品功能"
}
```

#### 请求参数说明

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| user_id | integer | 是 | 用户ID |
| message | string | 是 | 用户发送的消息内容 |

#### 返回格式

**成功情况（正常对话）**:
```json
{
  "status": "success",
  "response": "你好！我很高兴为你介绍我们的产品功能。我们的产品主要包含以下核心功能：\n\n1. 智能匹配：基于用户偏好和兴趣进行精准匹配\n2. 实时聊天：支持文字、语音等多种聊天方式\n3. AI助手：提供智能对话和情感支持\n4. 隐私保护：严格的数据加密和隐私保护机制\n\n你想了解哪个具体功能呢？",
  "summary": "",
  "error": null
}
```

**成功情况（对话结束，包含总结）**:
```json
{
  "status": "success",
  "response": "### 关键词提取\n- **休息和放松**: 睡大觉、晒太阳\n- **亲密关系**: 希望爱的人在身边\n\n### 生成关键词摘要\n你是一个重视休息和放松的人——喜欢通过自然的慰藉方式来充电，同时，你渴望有一个密的伴侣来共享这些美好的时刻。",
  "summary": "### 提问问题包\n现在，我将根据你分享的信息，为你生成三个适合初次见面时使用的交流问题，帮助你快速了解对方与你的兴趣匹配：\n\n1. **兴趣类问题**: 你最喜欢的户外活动是什么？有没有特别想去的地方？\n2. **生活理想类问题**: 你理想中的周末通常是怎么度过的？有没有什么特别的或者说需要的？\n3. **亲密关系类问题**: 在亲密关系中，你觉得\"被理解\"和\"被陪伴\"，哪个更重要？",
  "error": null
}
```

**AI服务失败情况**:
```json
{
  "status": "error",
  "response": "",
  "summary": "",
  "error": "AI服务调用失败"
}
```

#### 返回参数说明

| 参数名 | 类型 | 说明 |
|--------|------|------|
| status | string | 响应状态，"success" 或 "error" |
| response | string | AI的回复内容，失败时为空字符串 |
| summary | string | 问题包部分（当检测到对话结束时返回3个现场提问工具，否则为空字符串） |
| error | string/null | 错误信息，成功时为null |

#### 特殊情况说明

1. **5轮对话机制**: 严格按照5轮对话进行，AI必须在第5轮后输出总结，不得提前结束或延长
2. **对话结束检测**: 当AI回复包含总结性内容时，系统会自动分割回复和总结
3. **重试机制**: AI服务失败时自动重试，最多重试3次
4. **内存缓存**: 消息先存入内存，10秒后自动同步到数据库
5. **历史记录**: 自动获取用户历史对话作为上下文
6. **summary字段**: 在正常对话中为空字符串，当AI检测到对话结束（第5轮或包含总结关键词）时，会返回3个现场提问工具
7. **对话结束关键词**: 包括"关键词提取"、"你看重的关系特质"、"提问问题包"、"🌿 关键词"、"💖 你看重"、"🎯 提问"、"根据你分享的信息"、"基于我们的对话"、"我为你生成"、"以下三个问题"等及其相似表达
8. **输出分割**: 对话结束时，response字段包含关键词提取和摘要，summary字段包含3个现场提问工具

---

## 数据库格式说明

### AI聊天室表 (AI_chatroom)

```json
{
  "_id": "ObjectId('...')",
  "user_id": 12345,
  "chatroom_id": "chatroom_12345",
  "created_at": "2024-01-15T10:30:00.000Z",
  "updated_at": "2024-01-15T10:35:00.000Z",
  "message_count": 4,
  "last_message_time": "2024-01-15T10:35:00.000Z"
}
```

### AI消息表 (AI_message)

```json
{
  "_id": "ObjectId('...')",
  "message_id": "msg_1234567890",
  "chatroom_id": "chatroom_12345",
  "user_id": 12345,
  "message_type": "user",
  "content": "你好，我想了解一下你的服务",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "created_at": "2024-01-15T10:30:00.000Z",
  "is_summary": false,
  "summary_part": null
}
```

**AI消息的特殊字段说明**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| is_summary | boolean | 是否为总结性消息 |
| summary_part | string/null | 总结部分内容，非总结消息为null |

---

## 前端调用示例

### JavaScript/TypeScript 示例

```javascript
// 获取聊天历史
async function getChatHistory(userId) {
  try {
    const response = await fetch('/api/v1/ai/history', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId
      })
    });
    
    const data = await response.json();
    
    if (data.status === 'success') {
      console.log('聊天历史:', data.data);
      // 将元组数组转换为对象数组，便于前端使用
      const formattedHistory = data.data.map(([content, timestamp, senderId, displayName]) => ({
        content,
        timestamp,
        senderId,
        displayName,
        isUser: displayName === 'I'
      }));
      return formattedHistory;
    } else {
      console.error('获取历史失败:', data.error);
      return [];
    }
  } catch (error) {
    console.error('网络错误:', error);
    return [];
  }
}

// 发送AI聊天消息
async function sendAIMessage(userId, message) {
  try {
    const response = await fetch('/api/v1/ai/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        message: message
      })
    });
    
    const data = await response.json();
    
    if (data.status === 'success') {
      console.log('AI回复:', data.response);
      if (data.summary && data.summary.trim()) {
        console.log('对话总结:', data.summary);
      }
      return data;
    } else {
      console.error('AI服务失败:', data.error);
      return data;
    }
  } catch (error) {
    console.error('网络错误:', error);
    return {
      status: 'error',
      response: '',
      summary: '',
      error: '网络连接失败'
    };
  }
}

// 使用示例
const userId = 12345;

// 获取历史记录
getChatHistory(userId).then(history => {
  console.log('历史记录数量:', history.length);
});

// 发送消息
sendAIMessage(userId, "你好，我想了解一下你们的产品").then(result => {
  if (result.status === 'success') {
    console.log('收到回复:', result.response);
  }
});
```

### React Hook 示例

```javascript
import { useState, useEffect } from 'react';

// 自定义Hook：AI聊天
function useAIChat(userId) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // 获取聊天历史
  const loadHistory = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/ai/history', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId })
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        // 将元组数组转换为对象数组，便于前端使用
        const formattedHistory = data.data.map(([content, timestamp, senderId, displayName]) => ({
          content,
          timestamp,
          senderId,
          displayName,
          isUser: displayName === 'I'
        }));
        setHistory(formattedHistory);
        setError(null);
      } else {
        setError(data.error);
      }
    } catch (err) {
      setError('网络连接失败');
    } finally {
      setLoading(false);
    }
  };

  // 发送消息
  const sendMessage = async (message) => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          message: message
        })
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        // 添加用户消息到历史
        const userMessage = {
          content: message,
          timestamp: new Date().toISOString(),
          senderId: userId,
          displayName: 'I',
          isUser: true
        };
        
        // 添加AI回复到历史
        const aiMessage = {
          content: data.response,
          timestamp: new Date().toISOString(),
          senderId: 999, // AI用户ID
          displayName: 'AI Assistant',
          isUser: false
        };
        
        setHistory(prev => [...prev, userMessage, aiMessage]);
        setError(null);
        
        return {
          success: true,
          response: data.response,
          summary: data.summary || ""
        };
      } else {
        setError(data.error);
        return {
          success: false,
          error: data.error
        };
      }
    } catch (err) {
      const errorMsg = '网络连接失败';
      setError(errorMsg);
      return {
        success: false,
        error: errorMsg
      };
    } finally {
      setLoading(false);
    }
  };

  // 组件挂载时加载历史
  useEffect(() => {
    if (userId) {
      loadHistory();
    }
  }, [userId]);

  return {
    history,
    loading,
    error,
    sendMessage,
    loadHistory
  };
}

// 使用示例
function AIChatComponent({ userId }) {
  const { history, loading, error, sendMessage } = useAIChat(userId);
  const [inputMessage, setInputMessage] = useState('');

  const handleSend = async () => {
    if (!inputMessage.trim()) return;
    
    const result = await sendMessage(inputMessage);
    if (result.success) {
      setInputMessage('');
      console.log('发送成功，AI回复:', result.response);
      if (result.summary && result.summary.trim()) {
        console.log('对话总结:', result.summary);
      }
    } else {
      console.error('发送失败:', result.error);
    }
  };

  return (
    <div>
      <div className="chat-history">
        {history.map((msg, index) => (
          <div key={index} className={`message ${msg.isUser ? 'user' : 'ai'}`}>
            <span>{msg.content}</span>
            <small>{new Date(msg.timestamp).toLocaleString()}</small>
          </div>
        ))}
      </div>
      
      {loading && <div>正在处理...</div>}
      {error && <div className="error">错误: {error}</div>}
      
      <div className="input-area">
        <input
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="输入消息..."
          disabled={loading}
        />
        <button onClick={handleSend} disabled={loading || !inputMessage.trim()}>
          发送
        </button>
      </div>
    </div>
  );
}
```

---

## 错误处理建议

### 常见错误及处理方式

1. **网络连接失败**
   - 提示用户检查网络连接
   - 提供重试按钮

2. **AI服务暂时不可用**
   - 显示友好的错误提示
   - 建议用户稍后重试

3. **用户ID无效**
   - 检查用户登录状态
   - 引导用户重新登录

4. **消息内容过长**
   - 限制输入长度
   - 提示用户分段发送

### 错误状态码

| 状态码 | 说明 | 处理建议 |
|--------|------|----------|
| 200 | 成功 | 正常处理返回数据 |
| 400 | 请求参数错误 | 检查请求格式 |
| 500 | 服务器内部错误 | 稍后重试或联系客服 |

---

## 性能优化建议

1. **历史记录分页**: 对于历史记录较多的用户，建议实现分页加载
2. **消息缓存**: 在本地缓存最近的聊天记录，提升用户体验
3. **防抖处理**: 对发送消息按钮进行防抖处理，避免重复发送
4. **加载状态**: 显示适当的加载状态，提升用户体验

---

## 注意事项

1. **用户ID**: 确保传入的用户ID是有效的整数
2. **消息内容**: 消息内容不应为空，建议前端进行基本验证
3. **网络超时**: 建议设置合理的请求超时时间（建议30秒）
4. **错误重试**: 对于网络错误，建议实现自动重试机制
5. **数据同步**: 消息会先存入内存，10秒后同步到数据库，确保数据一致性

---

## 更新日志

- **v1.0.0**: 初始版本，包含基本的AI聊天功能
- **v1.1.0**: 添加对话结束检测和总结分割功能
- **v1.2.0**: 优化重试机制和错误处理
- **v1.3.0**: 完善内存缓存和数据库同步机制

---

*本文档最后更新时间: 2024年1月15日* 