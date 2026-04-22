from collections.abc import AsyncGenerator


def format_sse(event: str, data: str) -> str:
    return f"event: {event}\ndata: {data}\n\n"


async def sse_generator(generator: AsyncGenerator[str, None]) -> AsyncGenerator[str, None]:
     async for raw in generator:
        import json

        obj = json.loads(raw)
        yield format_sse(obj["event"], json.dumps(obj["data"], ensure_ascii=False))
