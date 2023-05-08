from pathlib import Path
from typing import Any, Awaitable, Coroutine, Mapping

from aiotinydb import AIOTinyDB

from src.environ import CONSOLE, TRUNCATE


class AsyncDatabaseInterFace(object):
    _uri = Path("./data/db/nosql.db")
    _kwargs = dict()

    async def __init__(self) -> None:
        async with AIOTinyDB(self._uri, **self._kwargs) as db:
            _ = db.table("pokemon")
            _ = db.table("generations")
            _ = db.table("pokedex")
            _ = db.table("cards_data")
            _ = db.table("cards_img")

    @classmethod
    async def truncate(cls) -> Coroutine[Any, Any, Awaitable[None]]:
        CONSOLE.log("[bold red]Truncating table...")

        async with AIOTinyDB(cls._uri, **cls._kwargs) as db:
            db.table("pokemon").truncate()
            db.table("generations").truncate()
            db.table("pokedex").truncate()
            db.table("cards_data").truncate()
            db.table("cards_img").truncate()

    @classmethod
    async def insert(
        cls, table: str, document: Mapping
    ) -> Coroutine[Any, Any, Awaitable[str]]:
        async with AIOTinyDB(cls._uri, **cls._kwargs) as db:
            db.table(table).insert(document)


if TRUNCATE:
    AsyncDatabaseInterFace.truncate()
