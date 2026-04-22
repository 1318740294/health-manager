# Quickstart: AI 健康管理对话助手

## 前置条件

- Docker 和 Docker Compose 已安装
- DeepSeek API Key（或 SiliconFlow API Key）

## 启动步骤

### 1. 克隆项目并配置

```bash
cd health-manager
cp .env.example .env
# 编辑 .env，填入你的 API Key：
# LLM_API_KEY=sk-your-deepseek-key
# LLM_BASE_URL=https://api.deepseek.com
# LLM_MODEL=deepseek-chat
```

### 2. 一键启动

```bash
docker-compose up --build
```

### 3. 访问应用

- 前端 H5 聊天界面: http://localhost:3000
- 后端 API 文档: http://localhost:8000/docs

## 使用验证

### 测试 1: 普通健康建议

在聊天框输入:
> 我最近总是失眠，有什么建议吗？

期望: AI 给出针对性的睡眠改善建议，有打字机效果。

### 测试 2: 睡眠数据查询（Function Calling）

在聊天框输入:
> 我昨天的睡眠怎么样？

期望:
1. 先显示"正在查询你的健康数据..."
2. 然后显示基于模拟睡眠数据的回复（如"昨晚深度睡眠2小时，总睡眠7小时"）

### 测试 3: 连续对话

接上一轮继续输入:
> 那我应该怎么做才能改善？

期望: AI 理解上文是关于睡眠的讨论，给出连贯的改善建议。

## 项目结构

```
health-manager/
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── app/
│   │   ├── main.py          # FastAPI 入口
│   │   ├── agent.py         # LLM Agent + Function Calling
│   │   ├── tools.py         # 工具定义 (get_user_sleep_data)
│   │   ├── session.py       # 对话记忆管理
│   │   └── sse.py           # SSE 流式响应
│   └── ...
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   ├── src/
│   │   ├── App.tsx          # 顶层容器 + 消息状态 + SSE 逻辑
│   │   ├── index.css        # 全局样式
│   │   └── components/
│   │       ├── ChatHeader.tsx    # NavBar 导航栏
│   │       ├── MessageList.tsx   # 消息列表（自动滚动）
│   │       ├── MessageBubble.tsx # 消息气泡（用户/AI）
│   │       ├── InputBar.tsx      # 输入框 + 发送按钮
│   │       └── LoadingDots.tsx   # loading 动画（3个跳动圆点）
│   └── ...
└── specs/
    └── 001-ai-health-assistant/
```

前端使用 [antd-mobile](https://mobile.ant.design/zh)（蚂蚁金服移动端 UI 组件库），基于 `NavBar`、`Input`、`Button` 等基础组件自定义实现对话界面。
