# Implementation Plan: AI 健康管理对话助手

**Feature**: AI 健康管理对话助手
**Branch**: main
**Created**: 2026/04/21
**Spec**: [spec.md](./spec.md)

---

## Technical Context

- **后端语言/框架**: Python 3.11+ / FastAPI
- **前端框架**: React 18+ / TypeScript / Vite + antd-mobile（蚂蚁金服移动端 UI 组件库）
- **LLM 对接**: DeepSeek API（OpenAI SDK 兼容），通过环境变量可切换
- **流式方案**: SSE (Server-Sent Events) via FastAPI StreamingResponse
- **对话记忆**: 后端内存字典，每 session 最近 5 轮（10 条 messages）
- **工具调用**: Function Calling 模式，注册 `get_user_sleep_data(date)` 模拟工具
- **容器化**: Docker + docker-compose（前后端分离）
- **包管理**: 后端 uv，前端 npm

---

## Constitution Check

本项目无 constitution 文件，跳过。

---

## Phase 0: Research — 完成

已产出 [research.md](./research.md)，技术选型已确定：
- LLM: DeepSeek API（首选）/ SiliconFlow（免费替代）
- 前端: antd-mobile（蚂蚁金服移动端 UI），使用 `NavBar`、`List`、`Input`、`Button` 等基础组件自定义实现对话界面
- 流式: SSE，两轮调用模式处理 Function Calling
- 记忆: 内存 dict + FIFO 淘汰

---

## Phase 1: Design — 完成

已产出:
- [data-model.md](./data-model.md) — 实体与数据关系
- [contracts/chat-api.md](./contracts/chat-api.md) — API 接口契约
- [quickstart.md](./quickstart.md) — 快速启动指南

---

## Phase 2: Implementation Plan

### 任务依赖图

```
T1: 项目骨架初始化（后端 pyproject.toml + 前端 vite init + 安装 antd-mobile）
 |
 ├─── T2: 后端 — Session 管理 (session.py)
 │     └── 无依赖，可立即开始
 │
 ├─── T3: 后端 — 工具定义 (tools.py)
 │     └── 无依赖，可立即开始
 │
 ├─── T4: 后端 — Agent + Function Calling (agent.py)
 │     └── 依赖 T2, T3
 │
 ├─── T5: 后端 — FastAPI 主入口 + SSE 端点 (main.py, sse.py)
 │     └── 依赖 T4
 │
 ├─── T6: 前端 — 对话界面组件 (App.tsx + components/)
 │     └── 依赖 T5（需要后端 API 地址）
 │
 ├─── T7: 前端 — 样式 (index.css + 组件样式)
 │     └── 依赖 T6
 │
 ├─── T8: Docker 容器化 (Dockerfile × 2 + docker-compose.yml)
 │     └── 依赖 T5, T6（前后端代码就绪后）
 │
 └── T9: 集成验证
       └── 依赖 T8
```

### T1: 项目骨架初始化

**产出**: `backend/pyproject.toml`, `frontend/` (Vite + React + TS 初始化)

- 后端: `uv init backend`，声明依赖 fastapi, uvicorn, openai, python-dotenv
- 前端: `npm create vite@latest frontend -- --template react-ts`，安装 `antd-mobile`
- 创建 `.env.example`

### T2: 后端 — Session 管理

**产出**: `backend/app/session.py`

- `ConversationSession` 类: 管理单个 session 的 messages 列表
- `SessionManager` 类: dict 存储所有 session，提供 `get_or_create(session_id)`
- System prompt: 定义 AI 健康助手的角色和行为规范
- FIFO 淘汰: 超过 10 条 user/assistant 消息时删除最早的
- 无外部依赖，纯 Python 实现

### T3: 后端 — 工具定义

**产出**: `backend/app/tools.py`

- `TOOLS` 列表: OpenAI Function Calling 格式的工具定义
  - `get_user_sleep_data(date: string)` — 查询指定日期的睡眠数据
- `get_user_sleep_data(date)` 函数: 返回硬编码的模拟数据
  - 深度睡眠 2 小时，浅度睡眠 3.5 小时，REM 1.5 小时，总 7 小时
  - 入睡 23:00，起床 06:30，质量评分 78

### T4: 后端 — Agent + Function Calling

**产出**: `backend/app/agent.py`

- `Agent` 类: 封装 LLM 调用逻辑
- `chat(session_id, message) -> AsyncGenerator[str, None]`:
  1. 获取 session，追加 user message
  2. 第一轮调用（非流式）: 发送 messages + tools，判断是否触发 tool_call
  3. 若触发 tool_call:
     - yield `tool_use` 事件
     - 执行工具函数，获取结果
     - yield `tool_result` 事件
     - 追加 tool message 到 session
     - 第二轮调用（流式）: 生成最终回复，逐 token yield
  4. 若未触发: 直接流式生成回复，逐 token yield
  5. 完成后 yield `done` 事件，保存完整消息到 session
- 支持通过环境变量配置 LLM_API_KEY, LLM_BASE_URL, LLM_MODEL

### T5: 后端 — FastAPI 主入口 + SSE

**产出**: `backend/app/main.py`, `backend/app/sse.py`

- `sse.py`: SSE 事件格式化工具函数
  - `format_sse_event(event, data) -> str`
  - `sse_response(generator) -> EventSourceResponse`
- `main.py`:
  - `POST /api/chat`: 接收 `{session_id, message}`，返回 SSE 流
  - `GET /api/health`: 健康检查
  - CORS 配置（允许前端跨域）

### T6: 前端 — 对话界面组件

**产出**: `frontend/src/App.tsx`, `frontend/src/components/` 下 4 个组件

- `App.tsx`: 顶层容器，管理 messages 状态 + session_id + SSE 逻辑
- `components/ChatHeader.tsx`: 使用 antd-mobile `NavBar` 显示"AI 健康助手"标题
- `components/MessageList.tsx`: 消息列表容器，自动滚动到底部，ref 管理
- `components/MessageBubble.tsx`: 单条消息气泡，区分用户（靠右蓝色）和 AI（靠左灰色）
- `components/InputBar.tsx`: 使用 antd-mobile `Input` + `Button` 实现底部输入区
- `handleSend` 逻辑:
  1. 添加用户消息到 messages state
  2. 显示 typing loading 状态
  3. POST `/api/chat`，用 `fetch` + `ReadableStream` 解析 SSE 流
  4. 逐 token 拼接 AI 回复，实时更新消息列表
  5. `done` 事件后结束 loading

### T7: 前端 — 样式

**产出**: `frontend/src/index.css`, `frontend/src/components/*.css`

- 全局: viewport 100vh, margin 0, flex column 布局
- 消息气泡: 用户消息蓝色靠右，AI 消息灰色靠左，圆角 + 阴影
- Loading 动画: CSS keyframes 实现 3 个跳动圆点
- 输入区: 固定底部，flex 布局，输入框 + 发送按钮
- 引入 `antd-mobile/dist/antd-mobile.css`

### T8: 前端 — 样式 + 移动端适配

**产出**: `frontend/src/styles/index.css`

- 移动端 H5 布局: viewport meta, 100vh, flex column
- 消息气泡样式: 用户蓝色靠右，AI 灰色靠左
- Loading 动画: 3 个跳动圆点
- 打字机效果: 无额外 CSS，靠 React 状态更新驱动
- 输入框: 固定底部，键盘弹出自适应

### T9: Docker 容器化

**产出**: `backend/Dockerfile`, `frontend/Dockerfile`, `frontend/nginx.conf`, `docker-compose.yml`, `.env.example`

- `backend/Dockerfile`: 基于 python:3.11-slim，uv 安装依赖，uvicorn 启动
- `frontend/Dockerfile`: 多阶段构建，node 编译 → nginx 托管静态文件
- `frontend/nginx.conf`: 代理 `/api` 到后端容器
- `docker-compose.yml`: 定义 backend + frontend 两个服务，前后端网络互通
- `.env.example`: LLM_API_KEY, LLM_BASE_URL, LLM_MODEL

### T10: 集成验证

**验证项**:

1. `docker-compose up --build` 能成功启动两个容器
2. 访问 http://localhost:3000 显示聊天界面
3. 发送"我最近失眠怎么办？"→ AI 回复健康建议（打字机效果）
4. 发送"我昨天睡了几个小时？"→ 先显示工具调用提示，再显示基于假数据的回复
5. 连续对话保持上下文
6. 5 轮后最早的对话被淘汰

---

## Assumptions

- 使用 DeepSeek API 作为默认 LLM，通过 `.env` 可切换到其他 OpenAI 兼容 API
- 前端通过 nginx 反向代理访问后端 API（Docker 环境内）
- 无用户认证系统，所有用户共享同一个模拟数据集
- 对话记忆仅在后端进程生命周期内有效，重启后丢失
- 移动端 H5 不做 PWA 离线支持

---

## Out of Scope (本次实施)

- 真实的用户认证和健康数据存储
- 数据库持久化
- 更多工具（运动、饮食等）
- 多模态输入（语音、图片）
- 生产级错误处理和日志
