import json
import logging
import os
from collections.abc import AsyncGenerator

from dotenv import load_dotenv
from openai import AsyncOpenAI

from .session import session_manager
from .tools import TOOLS, get_current_time, get_user_sleep_data

load_dotenv()

logger = logging.getLogger(__name__)

LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-chat")


class Agent:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)

    async def chat(self, session_id: str, message: str) -> AsyncGenerator[str, None]:
        session = session_manager.get_or_create(session_id)
        session.add_message("user", message)
        logger.info("[%s] 收到消息: %s", session_id, message)

        loop_count = 0
        while True:
            loop_count += 1
            logger.info("[%s] 第 %d 轮 LLM 调用, 历史消息数: %d", session_id, loop_count, len(session.messages))
            stream = await self.client.chat.completions.create(
                model=LLM_MODEL,
                messages=session.messages,
                tools=TOOLS,
                tool_choice="auto",
                stream=True,
            )

            tool_calls_accum: dict[int, dict] = {}
            finish_reason = None
            full_content = ""

            async for chunk in stream:
                choice = chunk.choices[0] if chunk.choices else None
                if not choice:
                    continue

                finish_reason = choice.finish_reason or finish_reason
                delta = choice.delta

                # 流式输出普通文本
                if delta and delta.content:
                    full_content += delta.content
                    yield json.dumps(
                        {"event": "token", "data": {"content": delta.content}},
                        ensure_ascii=False,
                    )

                # 累积 tool_call 的 delta
                if delta and delta.tool_calls:
                    for tc_delta in delta.tool_calls:
                        idx = tc_delta.index
                        if idx not in tool_calls_accum:
                            tool_calls_accum[idx] = {
                                "id": tc_delta.id or "",
                                "name": "",
                                "arguments": "",
                            }
                        if tc_delta.function:
                            if tc_delta.function.name:
                                tool_calls_accum[idx]["name"] = tc_delta.function.name
                            if tc_delta.function.arguments:
                                tool_calls_accum[idx]["arguments"] += tc_delta.function.arguments
                        if tc_delta.id:
                            tool_calls_accum[idx]["id"] = tc_delta.id

            if finish_reason != "tool_calls" or not tool_calls_accum:
                logger.info("[%s] LLM 不再请求工具调用, 流式输出完成, 回复长度: %d", session_id, len(full_content))
                break

            logger.info("[%s] LLM 请求 %d 个工具调用: %s", session_id, len(tool_calls_accum), [tc["name"] for tc in tool_calls_accum.values()])

            # 构造 assistant tool_calls 消息并加入历史
            tool_calls_msg = []
            for tc in tool_calls_accum.values():
                tool_calls_msg.append({
                    "id": tc["id"],
                    "type": "function",
                    "function": {
                        "name": tc["name"],
                        "arguments": tc["arguments"],
                    },
                })

            session.messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": tool_calls_msg,
            })

            # 逐个执行工具调用
            for tc in tool_calls_accum.values():
                func_name = tc["name"]
                func_args = json.loads(tc["arguments"] or "{}")

                yield json.dumps(
                    {"event": "tool_use", "data": {"tool": func_name, "status": "calling"}},
                    ensure_ascii=False,
                )

                if func_name == "get_current_time":
                    result = get_current_time()
                elif func_name == "get_user_sleep_data":
                    result = get_user_sleep_data(**func_args)
                else:
                    result = {"error": f"Unknown tool: {func_name}"}

                logger.info("[%s] 工具 %s 执行完成, 参数: %s, 结果: %s", session_id, func_name, func_args, result)

                yield json.dumps(
                    {"event": "tool_result", "data": {"tool": func_name, "result": result}},
                    ensure_ascii=False,
                )

                session.messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": json.dumps(result, ensure_ascii=False),
                })

            # 循环继续，带着工具结果再次调用 LLM

        session.add_message("assistant", full_content)
        yield json.dumps(
            {"event": "done", "data": {"content": full_content}},
            ensure_ascii=False,
        )
