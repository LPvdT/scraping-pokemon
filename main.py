import asyncio

from src.utils import entrypoint


def run() -> None:
    asyncio.run(entrypoint())
