import asyncio
import json
from sys import stdin
from typing import (
    Any,
    Awaitable,
    Coroutine,
    Literal,
    Optional,
    TextIO,
    Union,
)

import aiofiles
from playwright.async_api import (
    Browser,
    Locator,
    Page,
    async_playwright,
)
from rich.console import Console

import src.environ as environ
import src.scraping as scraping


async def save_screenshot(
    element: Union[Locator, Page],
    filename: str,
    img_type: Literal["jpg", "png"],
    full_page: bool = False,
) -> Coroutine[Any, Any, Awaitable[None]]:
    idx = filename.find(".")

    if idx >= 0:
        filename = filename[:idx]

    await element.screenshot(
        type=img_type,
        path=f"./data/static/img/{filename}.{img_type}",
        full_page=full_page,
    )


async def save_json(
    obj: Any, filename: str
) -> Coroutine[Any, Any, Awaitable[None]]:
    idx = filename.find(".")

    if idx >= 0:
        filename = filename[0:idx]

    async with aiofiles.open(
        file=f"./data/static/out/{filename}.json",
        mode="w",
        encoding="utf-8",
    ) as f:
        await f.write(
            json.dumps(
                obj, indent=2, sort_keys=True, ensure_ascii=False
            )
        )


async def navigate(
    url: str,
    browser: Optional[Browser] = None,
    page: Optional[Page] = None,
) -> Coroutine[Any, Any, Awaitable[Page]]:
    if not page and not browser:
        raise TypeError("Either 'browser' or 'page' must be provided")

    if page:
        await page.goto(url)
    else:
        page = await browser.new_page()
        await page.goto(url)

    # Log
    environ.CONSOLE.rule("[bold]Page title")
    environ.CONSOLE.log(await page.title())

    return page


async def dump_console_recording(
    console: Console, title: str, type: Literal["svg", "html"]
) -> Coroutine[Any, Any, Awaitable[None]]:
    params = dict(
        path=f"./data/static/logs/{title}.svg",
        title=title.title(),
        clear=False,
    )

    if type == "svg":
        console.save_svg(**params)
    elif type == "html":
        console.save_html(
            path=params["path"].replace(".svg", ".html"),
            clear=params["clear"],
        )
    else:
        raise ValueError(f"'{type}' is not a valid argument for type")


async def teardown(
    browser: Browser,
) -> Coroutine[Any, Any, Awaitable[None]]:
    if environ.KEEP_ALIVE:
        environ.CONSOLE.log(">> Press CTRL-D to stop")

        reader = asyncio.StreamReader()
        pipe: TextIO = stdin
        loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()

        await loop.connect_read_pipe(
            lambda: asyncio.StreamReaderProtocol(reader), pipe
        )
    else:
        await browser.close()


async def entrypoint() -> Coroutine[Any, Any, Awaitable[None]]:
    async with async_playwright() as backend:
        await scraping.main_coroutine(backend)
