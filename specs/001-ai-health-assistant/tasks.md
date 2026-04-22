# Tasks: AI 健康管理对话助手 — 前端重构（antd-mobile）

**Feature**: AI 健康管理对话助手
**Branch**: main
**Created**: 2026/04/21
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

---

## Phase 1: Setup（项目骨架初始化）

- [x] T001 [P] 初始化后端项目骨架：创建 `backend/` 目录、`backend/pyproject.toml`（声明依赖 fastapi, uvicorn, openai, python-dotenv）、`backend/app/__init__.py`
- [x] T002 [P] 初始化前端项目骨架：`npm create vite@latest frontend -- --template react-ts`，安装 `antd-mobile`
- [x] T003 [P] 创建 `.env.example`，包含 `LLM_API_KEY=`、`LLM_BASE_URL=https://api.deepseek.com`、`LLM_MODEL=deepseek-chat`

---

## Phase 2: Foundational（后端核心模块 — 已完成）

- [x] T004 [P] 实现对话记忆管理：创建 `backend/app/session.py`
- [x] T005 [P] 实现工具定义与模拟数据：创建 `backend/app/tools.py`
- [x] T006 实现 LLM Agent + Function Calling：创建 `backend/app/agent.py`
- [x] T007 实现 SSE 流式响应 + FastAPI 主入口：创建 `backend/app/sse.py`、`backend/app/main.py`

---

## Phase 3: 前端重构 — 去除 ChatUI，使用 antd-mobile 自定义实现

**目标**: 用 antd-mobile 基础组件（NavBar、Input、Button）自定义实现移动端对话界面，替换掉有兼容问题的 @chatui/core

### T008: 安装 antd-mobile，移除 @chatui/core

- [ ] T008 卸载 `@chatui/core`，安装 `antd-mobile`：`npm uninstall @chatui/core && npm install antd-mobile`

### T009: 创建对话界面组件

- [ ] T009 [P] 创建 `frontend/src/components/ChatHeader.tsx`：使用 antd-mobile `NavBar` 组件，显示"AI 健康助手"标题
- [ ] T010 [P] 创建 `frontend/src/components/MessageBubble.tsx`：消息气泡组件，接收 `role`(user/assistant/system) 和 `content` props，用户消息靠右蓝色，AI 消息靠左灰色，系统消息居中浅色
- [ ] T011 [P] 创建 `frontend/src/components/MessageList.tsx`：消息列表容器，接收 `messages` 数组和 `isTyping` 状态，使用 `useRef` + `useEffect` 实现自动滚动到底部，typing 时显示 LoadingDots
- [ ] T012 [P] 创建 `frontend/src/components/LoadingDots.tsx`：CSS 动画实现 3 个跳动圆点的 loading 指示器
- [ ] T013 创建 `frontend/src/components/InputBar.tsx`：使用 antd-mobile `Input` + `Button` 组成底部输入区，固定在视口底部，flex 布局

### T014: 重写 App.tsx — 消息状态 + SSE 流式对接

- [ ] T014 重写 `frontend/src/App.tsx`：
      - `useState<ChatMessage[]>` 管理消息列表
      - `useRef<string>` 存储 session_id（`crypto.randomUUID()`）
      - `useState<boolean>` 管理 isTyping 状态
      - `handleSend(content)`:
        1. `setMessages(prev => [...prev, { role: 'user', content }])`
        2. `setIsTyping(true)`
        3. `fetch('/api/chat', { method: 'POST', body: JSON.stringify({ session_id, message }) })`
        4. `response.body.getReader()` 逐行解析 SSE 流
        5. `token` 事件 → 更新最后一条 assistant 消息的 content（或创建新消息）
        6. `tool_use` 事件 → 添加 system 消息"正在查询你的健康数据..."
        7. `done` 事件 → `setIsTyping(false)`
        8. `error` 事件 → 添加 system 错误消息
      - 渲染: `ChatHeader` + `MessageList` + `InputBar`

### T015: 样式

- [ ] T015 创建 `frontend/src/index.css`：全局样式（viewport 100vh, flex column）
- [ ] T016 创建 `frontend/src/components/MessageBubble.css`：消息气泡样式（用户蓝色靠右圆角、AI 灰色靠左圆角、系统消息居中浅色）
- [ ] T017 创建 `frontend/src/components/LoadingDots.css`：`@keyframes bounce` 跳动圆点动画
- [ ] T018 创建 `frontend/src/components/InputBar.css`：底部输入区样式（固定定位、flex、阴影）
- [ ] T019 修改 `frontend/src/main.tsx`：导入 `antd-mobile/dist/antd-mobile.css`

### T020: 清理旧文件

- [ ] T020 删除 `frontend/src/assets/` 目录下的 Vite 默认资源文件（hero.png 等），删除 `frontend/src/App.css`（如存在）

---

## Phase 4: 验证

- [ ] T021 TypeScript 类型检查通过：`npx tsc --noEmit`
- [ ] T022 前端构建成功：`npx vite build`
- [ ] T023 启动前端 dev server，访问 http://localhost:5173 显示对话界面

---

## 依赖关系

```
Phase 1 (T001-T003)  —  已完成
Phase 2 (T004-T007)  —  已完成（后端不变）
    │
Phase 3 重构:
  T008 (卸载/安装依赖)  ← 先执行
    │
  T009-T013 (4个组件)  ← 并行创建
    │
  T014 (App.tsx 重写)  ← 依赖组件
    │
  T015-T019 (样式)     ← 并行创建
    │
  T020 (清理)          ← 最后
    │
Phase 4 验证 (T021-T023)
```

## 并行执行机会

- **T009-T012**: 4 个组件文件互不依赖，完全并行
- **T015-T018**: 4 个样式文件互不依赖，完全并行
