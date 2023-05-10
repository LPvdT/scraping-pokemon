import asyncio
from typing import Any, Coroutine
import aiofiles
import aiohttp
import json
from pathlib import Path


async def save_img(url: str) -> Coroutine[Any, Any, None]:
    filename = (
        f"./data/static/img/{Path(url).stem.title()}.{Path(url).suffix}"
    )

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            if res.status == 200:
                payload = await res.read()
                async with aiofiles.open(filename, "wb+") as f:
                    await f.write(payload)


if __name__ == "__main__":
    with open(
        "./data/static/out/data_pokedex_cards_img.json", "r+"
    ) as f:
        data = json.load(f)

    tasks = [save_img(d["img_src"][0]) for d in data]

    asyncio.gather(*tasks)
