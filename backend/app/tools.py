import datetime


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前服务器的日期和时间。当用户提到相对日期（如昨天、上周）时，先调用此工具确认具体日期，再查询数据。",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_user_sleep_data",
            "description": "查询用户指定日期的睡眠数据，包括总睡眠时长、深度睡眠、浅度睡眠、REM睡眠、入睡/起床时间和睡眠质量评分。",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "查询日期，格式为 YYYY-MM-DD，例如 '2026-04-20'",
                    }
                },
                "required": ["date"],
            },
        },
    },
]


def get_current_time() -> dict:
    now = datetime.datetime.now()
    return {
        "current_datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
        "date": now.strftime("%Y-%m-%d"),
        "weekday": now.strftime("%A"),
    }


def get_user_sleep_data(date: str) -> dict:
    """返回模拟睡眠数据"""
    return {
        "date": date,
        "total_hours": 7.0,
        "deep_hours": 2.0,
        "light_hours": 3.5,
        "rem_hours": 1.5,
        "sleep_time": "23:00",
        "wake_time": "06:30",
        "quality_score": 78,
    }
