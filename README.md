# AI 健康管理对话助手

基于 LLM 的健康管理对话助手，支持流式对话、Function Calling 工具调用，覆盖睡眠、运动、饮食、心理等健康领域。

## 使用示例

> 视频文件：`[assets/使用示例.mov](assets/使用示例.mov)`

## 技术栈


|     | 前端                    | 后端                    |
| --- | --------------------- | --------------------- |
| 框架  | React 18 + TypeScript | FastAPI               |
| UI  | antd-mobile 5         | -                     |
| 构建  | Vite 8                | -                     |
| 包管理 | npm                   | uv                    |
| 通信  | SSE 流式传输              | OpenAI SDK (DeepSeek) |


## 项目结构

```
health-manager/
├── start.sh               # 一键启动脚本
├── docker-compose.yml
├── .env.example             # 环境变量模板
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI 入口
│   │   ├── agent.py         # LLM Agent（支持 Function Calling）
│   │   ├── tools.py         # 工具定义（时间查询、睡眠数据）
│   │   ├── session.py       # 会话管理
│   │   └── sse.py           # SSE 格式化
│   └── pyproject.toml
├── frontend/
│   └── src/
│       ├── App.tsx           # 主组件，SSE 流式接收
│       └── components/       # ChatHeader / MessageList / MessageBubble / InputBar
└── assets/
```

## 快速开始

### 1. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入你的 API Key
```


| 变量             | 默认值                        | 说明             |
| -------------- | -------------------------- | -------------- |
| `LLM_API_KEY`  | -                          | LLM 服务 API Key |
| `LLM_BASE_URL` | `https://api.deepseek.com` | LLM API 地址     |
| `LLM_MODEL`    | `deepseek-chat`            | 模型名称           |


支持任何兼容 OpenAI SDK 的 LLM 服务，替换上述配置即可。

### 2. 启动服务

**方式一：启动脚本（推荐）**

```bash
./start.sh
```

前端：[http://localhost:5173](http://localhost:5173)　　 后端：[http://localhost:8000](http://localhost:8000)

**方式二：Docker Compose**

```bash
docker-compose up --build
```

前端：[http://localhost:3000](http://localhost:3000)　　 后端：[http://localhost:8000](http://localhost:8000)

### 3. 单独启动

```bash
# 后端
cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 前端
cd frontend && npm run dev
```

## API 接口


| 方法     | 路径            | 说明               |
| ------ | ------------- | ---------------- |
| `POST` | `/api/chat`   | 发送消息，返回 SSE 流式响应 |
| `GET`  | `/api/health` | 健康检查             |


### POST /api/chat

请求体：

```json
{
  "session_id": "uuid",
  "message": "你好"
}
```

SSE 事件流：`token`（文本流）、`tool_use`（工具调用）、`tool_result`（工具结果）、`done`（完成）、`error`（错误）。