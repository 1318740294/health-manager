import time
import uuid

SYSTEM_PROMPT = (
    "你是一位专业的 AI 健康管理助手。你的职责是：\n"
    "1. 根据用户的健康问题提供科学、实用的建议，涵盖睡眠、运动、饮食、心理健康等领域。\n"
    "2. 当用户需要查询个人健康数据时，调用可用工具获取数据并给出解读。\n"
    "3. 保持友善、自然的对话风格，像朋友一样关心用户的健康。\n"
    "4. 如果问题涉及医疗诊断或处方，请明确告知你不是医生，建议用户咨询专业医疗人员。\n"
    "5. 如果不确定用户意图，请主动追问而不是猜测。\n"
    "请用中文回复。"
)

MAX_MESSAGES = 10  # 最多保留 10 条 user/assistant 消息（5 轮）


class ConversationSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.messages: list[dict] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        self.created_at = time.time()
        self.updated_at = time.time()

    def add_message(self, role: str, content: str, **kwargs):
        msg = {"role": role, "content": content}
        msg.update(kwargs)
        self.messages.append(msg)
        self.updated_at = time.time()
        self._evict()

    def _evict(self):
        """FIFO 淘汰：超过 MAX_MESSAGES 条非 system 消息时删除最早的"""
        non_system = [m for m in self.messages if m["role"] != "system"]
        if len(non_system) > MAX_MESSAGES:
            excess = len(non_system) - MAX_MESSAGES
            removed = 0
            new_messages = [self.messages[0]]  # 保留 system prompt
            for msg in self.messages[1:]:
                if msg["role"] != "system" and removed < excess:
                    removed += 1
                else:
                    new_messages.append(msg)
            self.messages = new_messages


class SessionManager:
    def __init__(self):
        self._sessions: dict[str, ConversationSession] = {}

    def get_or_create(self, session_id: str) -> ConversationSession:
        if session_id not in self._sessions:
            self._sessions[session_id] = ConversationSession(session_id)
        return self._sessions[session_id]


session_manager = SessionManager()
