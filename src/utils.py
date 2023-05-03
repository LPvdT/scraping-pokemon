import asyncio
from sys import stdin
from typing import Any, Awaitable, Coroutine, Literal, Optional, TextIO

from playwright.async_api import Browser, Page, async_playwright
from rich.console import Console

from src.environ import CONSOLE, KEEP_ALIVE
from src.scraping import main_coroutine


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
    CONSOLE.rule("[bold]Page title")
    CONSOLE.log(await page.title())

    return page


async def dump_console_recording(
    console: Console, title: str, type: Literal["svg", "html"]
) -> Coroutine[Any, Any, Awaitable[None]]:
    params = dict(
        path=f"./data/static/logs/{title}.svg",
        title=title.title(),
    )

    if type == "svg":
        console.save_svg(**params)
    elif type == "html":
        console.save_html(
            **params.update(
                path=params["path"].replace(".svg", ".html")
            )
        )
    else:
        raise ValueError(f"'{type}' is not a valid argument for type")


async def teardown(
    browser: Browser,
) -> Coroutine[Any, Any, Awaitable[None]]:
    if KEEP_ALIVE:
        CONSOLE.log(">> Press CTRL-D to stop")

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
        await main_coroutine(backend)
