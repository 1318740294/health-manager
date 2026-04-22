# Data Model: AI 健康管理对话助手

## 实体定义

### Message（对话消息）

对话中的单条消息，是系统的核心数据单元。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| role | string | yes | 消息角色: "system" / "user" / "assistant" / "tool" |
| content | string | yes | 消息文本内容（tool 角色为工具返回结果） |
| tool_calls | list | no | 模型请求调用的工具列表（仅 assistant 角色） |
| tool_call_id | string | no | 关联的工具调用 ID（仅 tool 角色） |

**验证规则**:
- role 必须为 system / user / assistant / tool 之一
- user 消息 content 不可为空
- tool 消息必须携带 tool_call_id
- assistant 消息中 tool_calls 和 content 互斥（有工具调用时 content 为空）

### ConversationSession（对话会话）

一次用户与 AI 的连续对话，用于管理上下文。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| session_id | string (UUID) | yes | 前端生成的会话唯一标识 |
| messages | list[Message] | yes | 对话历史，最多保留 10 条（5 轮） |
| created_at | float | yes | 会话创建时间戳 |
| updated_at | float | yes | 最后更新时间戳 |

**状态转换**:
- 新建: messages 仅含 system prompt
- 活跃: 每次交互追加 user + assistant 消息对
- 淘汰: 超过 10 条后从头部删除最早的非 system 消息

### SleepData（睡眠数据 - 模拟）

模拟工具 `get_user_sleep_data` 返回的假数据结构。

| 字段 | 类型 | 说明 |
|------|------|------|
| date | string | 查询日期 (YYYY-MM-DD) |
| total_hours | float | 总睡眠时长（小时） |
| deep_hours | float | 深度睡眠时长（小时） |
| light_hours | float | 浅度睡眠时长（小时） |
| rem_hours | float | REM 睡眠时长（小时） |
| sleep_time | string | 入睡时间 |
| wake_time | string | 起床时间 |
| quality_score | int | 睡眠质量评分 (0-100) |

**验证规则**:
- deep_hours + light_hours + rem_hours 应 ≤ total_hours
- quality_score 范围 0-100

### ToolDefinition（工具定义）

注册给 LLM 的 Function Calling 工具描述。

| 字段 | 类型 | 说明 |
|------|------|------|
| type | string | 固定 "function" |
| function.name | string | 工具名称，如 "get_user_sleep_data" |
| function.description | string | 工具功能描述 |
| function.parameters | object | JSON Schema 格式的参数定义 |

## 数据关系

```
ConversationSession
  └── messages: [Message, Message, ...]  (1:N，最多10条)

ToolDefinition (静态注册)
  └── 执行后生成 SleepData，包装为 tool Message
```

## 内存存储结构

```python
# 后端进程内存中
sessions: dict[str, list[Message]] = {}
# key = session_id, value = messages 列表（含 system prompt）

# 淘汰策略: len(messages) > 11 时删除 messages[1]（跳过 index 0 的 system prompt）
```
