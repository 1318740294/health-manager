# API Contract: AI 健康管理对话助手

## 端点概览

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/chat | 发送消息，SSE 流式返回 AI 回复 |
| GET | /api/health | 健康检查 |

---

## POST /api/chat

发送用户消息，通过 SSE 流式接收 AI 回复。

### 请求

```http
POST /api/chat
Content-Type: application/json

{
  "session_id": "uuid-string",
  "message": "我昨天的睡眠怎么样？"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| session_id | string | yes | 会话 ID，首次使用时前端生成 UUID |
| message | string | yes | 用户输入的自然语言消息 |

### 响应: SSE 流

Content-Type: `text/event-stream`

#### 正常回复（直接文本生成）

```
event: token
data: {"content": "你"}

event: token
data: {"content": "好，"}

event: token
data: {"content": "根据你的问题..."}

event: done
data: {"content": "完整回复文本"}
```

#### 涉及工具调用的回复

```
event: tool_use
data: {"tool": "get_user_sleep_data", "status": "calling"}

event: tool_result
data: {"tool": "get_user_sleep_data", "result": {"total_hours": 7, "deep_hours": 2, ...}}

event: token
data: {"content": "根据你的睡眠数据..."}

event: token
data: {"content": "昨晚你睡了7小时..."}

event: done
data: {"content": "完整回复文本"}
```

#### 错误

```
event: error
data: {"message": "LLM API 调用失败", "code": "LLM_ERROR"}
```

### SSE 事件类型

| event | data 结构 | 说明 |
|-------|-----------|------|
| token | `{"content": "单个token"}` | 流式文本片段 |
| done | `{"content": "完整文本"}` | 回复结束，携带完整内容 |
| tool_use | `{"tool": "函数名", "status": "calling"}` | 通知前端正在调用工具 |
| tool_result | `{"tool": "函数名", "result": {...}}` | 工具执行结果 |
| error | `{"message": "错误信息", "code": "错误码"}` | 错误通知 |

### 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 正常流式响应 |
| 400 | 请求参数错误 |
| 500 | 服务端内部错误（LLM 调用失败等） |

---

## GET /api/health

### 响应

```json
{
  "status": "ok",
  "timestamp": "2026-04-21T10:00:00Z"
}
```

---

## 前端-后端交互协议（基于 antd-mobile 自定义实现）

### 前端发送消息流程

1. 用户输入消息 → 点击发送按钮 → `handleSend` 触发
2. `setMessages(prev => [...prev, { role: 'user', content: val }])` 添加用户消息
3. `setIsTyping(true)` 显示 loading 动画（CSS 3 个跳动圆点）
4. `fetch('/api/chat', ...)` 发送 POST 请求，用 `response.body.getReader()` 解析 SSE 流
5. 收到 `token` 事件 → 逐 token 拼接到当前 AI 消息，更新 state
6. 收到 `tool_use` 事件 → 添加系统提示消息"正在查询你的健康数据..."
7. 收到 `done` 事件 → `setIsTyping(false)`，完成

### 前端组件结构

| 组件 | 使用的 antd-mobile 组件 | 说明 |
|------|------------------------|------|
| ChatHeader | `NavBar` | 顶部导航栏，显示"AI 健康助手" |
| MessageList | 自定义 div + flex | 消息列表，自动滚动 |
| MessageBubble | 自定义 div + CSS | 消息气泡（用户/AI 两种样式） |
| InputBar | `Input` + `Button` | 底部输入框 + 发送按钮 |
| LoadingDots | 自定义 div + CSS | 3 个跳动圆点 loading 动画 |

### 前端消息状态模型

```typescript
interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}
```

- `messages: ChatMessage[]` — useState 管理
- 用户消息: `{ role: 'user', content: val }`
- AI 消息: `{ role: 'assistant', content: '' }`，初始为空，逐 token 更新
- 系统提示: `{ role: 'system', content: '正在查询你的健康数据...' }`

### 首字延迟优化

- 发送消息后立即 `setIsTyping(true)`
- CSS 动画实现 3 个跳动圆点（`@keyframes bounce`）
- 收到第一个 `token` 事件后 `setIsTyping(false)`，开始显示文本

### Session 管理

- 前端首次加载时生成 `session_id`（`crypto.randomUUID()`）
- 存储在 React state 中，刷新页面后丢失（符合 demo 级需求）
- 后端根据 `session_id` 查找或创建会话上下文
