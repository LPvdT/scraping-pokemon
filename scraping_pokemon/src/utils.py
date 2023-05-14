import asyncio
import json
from datetime import datetime
from hashlib import sha1, sha256
from pathlib import Path
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
import aiohttp
from playwright.async_api import (
    Browser,
    Locator,
    Page,
    async_playwright,
)

import scraping_pokemon.src.environ as environ
import scraping_pokemon.src.scraping as scraping


async def save_img(url: str) -> Coroutine[Any, Any, None]:
    filename = f"./data/static/img/pokemon/{Path(url).stem.title()}{Path(url).suffix}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            if res.status == 200:
                payload = await res.read()

                async with aiofiles.open(filename, "wb+") as f:
                    await f.write(payload)

                    # Log
                    environ.CONSOLE.log(
                        f"Saved image: '{Path(url).stem.title()}{Path(url).suffix}'"
                    )


async def generate_hash(
    value: Union[str, int, float, list, tuple, set],
    kind: Literal["sha-1", "sha-256"] = "sha-1",
):
    if isinstance(value, (list, tuple, set)):
        _value = "|".join(str(value)).encode("utf-8")
    elif isinstance(value, (int, float)):
        _value = str(value).encode("utf-8")
    else:
        raise ValueError(f"'{value}' is not supported")

    if kind == "sha-1":
        hashed = sha1(_value)
    elif kind == "sha-256":
        hashed = sha256(_value)
    else:
        raise ValueError(f"'{kind}' is not supported")

    return hashed.hexdigest()


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
        path=f"./data/static/img/screenshots/{filename}.{img_type}",
        full_page=full_page,
    )

    # Log
    environ.CONSOLE.log(
        f"Saved screenshot for '{filename}' page/element."
    )


async def save_json(
    obj: Any, filename: str, sort: bool = False
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
                obj, indent=2, sort_keys=sort, ensure_ascii=False
            )
        )

        # Log
        environ.CONSOLE.log(f"Created JSON dump for '{filename}'.")


def clean_text(text: str) -> str:
    _text = text

    for sub in ["\u2019", "\u2018", "\u2019"]:
        _text = _text.replace(sub, "\u0060")

    _text = _text.replace("\u2013", "\u002d")

    return _text


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
    environ.CONSOLE.log(f"Navigating to: {url}")

    # Set page timeout
    page.set_default_timeout(environ.PAGE_TIMEOUT)

    return page


async def dump_console_recording(
    title: str, type: Literal["svg", "html"]
) -> Coroutine[Any, Any, Awaitable[None]]:
    params = dict(
        path=f"./data/static/logs/{title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.svg",
        title=title.title(),
        clear=False,
    )

    # Log
    environ.CONSOLE.log(
        f"Dumping console logs: [b i]{type.upper()}[/b i] format..."
    )

    if type == "svg":
        environ.CONSOLE.save_svg(**params)
    elif type == "html":
        environ.CONSOLE.save_html(
            path=params["path"].replace(".svg", ".html"),
            clear=params["clear"],
        )
    else:
        raise ValueError(f"'{type}' is not a valid argument for type")


async def teardown(
    browser: Browser,
) -> Coroutine[Any, Any, Awaitable[None]]:
    # Log
    environ.CONSOLE.log("Initiating browser teardown...")

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
        # Log
        environ.CONSOLE.log("Initiating async browser context...")

        await scraping.main_coroutine(backend)
