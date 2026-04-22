import json
import os
from collections.abc import AsyncGenerator

from dotenv import load_dotenv
from openai import OpenAI

from .session import session_manager
from .tools import TOOLS, get_user_sleep_data

load_dotenv()

LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-chat")


class Agent:
    def __init__(self):
        self.client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)

    def chat(self, session_id: str, message: str) -> AsyncGenerator[str, None]:
        session = session_manager.get_or_create(session_id)
        session.add_message("user", message)

        # 第一轮：非流式，判断是否触发 tool_call
        response = self.client.chat.completions.create(
            model=LLM_MODEL,
            messages=session.messages,
            tools=TOOLS,
            tool_choice="auto",
            stream=False,
        )

        choice = response.choices[0]
        assistant_msg = choice.message

        if assistant_msg.tool_calls:
            # 模型请求调用工具
            tool_call = assistant_msg.tool_calls[0]
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments)

            # 将 assistant 的 tool_calls 消息加入历史
            session.messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": func_name,
                            "arguments": tool_call.function.arguments,
                        },
                    }
                ],
            })

            yield json.dumps(
                {"event": "tool_use", "data": {"tool": func_name, "status": "calling"}},
                ensure_ascii=False,
            )

            # 执行工具
            if func_name == "get_user_sleep_data":
                result = get_user_sleep_data(**func_args)
            else:
                result = {"error": f"Unknown tool: {func_name}"}

            yield json.dumps(
                {"event": "tool_result", "data": {"tool": func_name, "result": result}},
                ensure_ascii=False,
            )

            # 将工具结果作为 tool message 加入历史
            session.messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, ensure_ascii=False),
            })

            # 第二轮：流式生成最终回复
            stream = self.client.chat.completions.create(
                model=LLM_MODEL,
                messages=session.messages,
                stream=True,
            )

            full_content = ""
            for chunk in stream:
                delta = chunk.choices[0].delta if chunk.choices else None
                if delta and delta.content:
                    full_content += delta.content
                    yield json.dumps(
                        {"event": "token", "data": {"content": delta.content}},
                        ensure_ascii=False,
                    )

            session.add_message("assistant", full_content)
            yield json.dumps(
                {"event": "done", "data": {"content": full_content}},
                ensure_ascii=False,
            )

        else:
            # 未触发工具调用，直接流式生成回复
            # 先回退 user message（因为第一轮已经加了），重新发起流式请求
            # 实际上 messages 里已经有 user message，直接流式即可
            # 但第一轮是非流式的，需要重新流式生成
            # 简化处理：直接用第一轮的非流式结果作为回复
            content = assistant_msg.content or ""
            session.add_message("assistant", content)
            yield json.dumps(
                {"event": "token", "data": {"content": content}},
                ensure_ascii=False,
            )
            yield json.dumps(
                {"event": "done", "data": {"content": content}},
                ensure_ascii=False,
            )
