# Research: AI 健康管理对话助手

## 技术选型决策

### 决策 1: LLM API 选型

- **决策**: 使用 DeepSeek API（`deepseek-chat` 模型），通过环境变量支持切换到 SiliconFlow
- **理由**:
  - DeepSeek-V3.2 对 Function Calling 支持完善，支持 strict mode
  - 中国公司，中文理解能力强
  - 成本极低（$0.07/次典型对话）
  - OpenAI SDK 兼容，集成成本最小
  - 128K 上下文窗口
- **备选**: SiliconFlow（免费 Qwen3.5-4B 模型，但小模型 Function Calling 可能不稳定）
- **集成方式**: 标准 `openai` Python SDK，通过 `base_url` 切换

### 决策 2: SSE 流式方案

- **决策**: 后端使用 FastAPI 的 `StreamingResponse` + `EventSourceResponse`，前端使用 `EventSource` / `fetch` + `ReadableStream`
- **理由**:
  - SSE 天然适合 LLM 逐 token 输出的单向推送场景
  - 比 WebSocket 更简单，无需双向通信
  - FastAPI 原生支持异步流
  - 浏览器 EventSource API 成熟
- **备选**: WebSocket（过度设计，不需要双向通信）
- **流式中的 Function Calling**: 当检测到 tool_call 时，先返回工具调用信号（前端显示"正在查询数据..."），执行工具后再发起第二轮流式请求

### 决策 3: React Chat UI

- **决策**: 使用 antd-mobile 基础组件自定义实现对话界面，不使用第三方聊天库
- **理由**:
  - @chatui/core 存在 CJS/ESM 兼容问题，named export 在某些构建环境下不可用
  - antd-mobile 提供成熟的移动端基础组件（NavBar、Input、Button），足够搭建对话界面
  - 自定义实现更灵活，容易控制 SSE 流式对接和 typing 动画
- **组件结构**: App → ChatHeader(NavBar) + MessageList + MessageBubble + InputBar(Input+Button) + LoadingDots

### 决策 4: 多轮对话记忆管理

- **决策**: 后端内存中以字典维护每个 session 的最近 5 轮对话（user + assistant 各一条为一轮）
- **理由**:
  - 需求明确"在内存中维护即可"
  - 5 轮 = 10 条 messages（user/assistant 交替）
  - Python 字典 + list 足够，无需 Redis
  - 重启丢失，符合 demo 级别要求
- **session 标识**: 前端生成 UUID 作为 session_id，每次请求携带

### 决策 5: Function Calling 实现模式

- **决策**: 采用两轮调用模式
  1. 第一轮：发送用户消息 + tools 定义，模型返回 tool_call
  2. 后端拦截 tool_call，执行 `get_user_sleep_data(date)`，将结果作为 tool message 追加
  3. 第二轮：带着工具执行结果再次请求，模型生成最终回复
- **理由**:
  - 这是 OpenAI Function Calling 标准模式
  - DeepSeek 完全兼容此模式
  - 工具执行结果需要二次生成，无法一步到位
- **SSE 衔接**: 第一轮非流式（判断是否调用工具），第二轮流式（生成最终回复）

## 依赖分析

| 依赖 | 用途 | 选型 |
|------|------|------|
| Python 3.11+ | 后端运行时 | 最新稳定版 |
| FastAPI | Web 框架 | 异步 + SSE 支持 |
| uvicorn | ASGI 服务器 | FastAPI 默认 |
| openai | LLM SDK | DeepSeek 兼容 |
| uv | Python 包管理 | 快速、现代 |
| React 18+ | 前端框架 | 移动端 H5 |
| Vite | 前端构建 | 快速开发 |
| TypeScript | 类型安全 | 减少运行时错误 |
| Docker | 容器化 | 统一环境 |
