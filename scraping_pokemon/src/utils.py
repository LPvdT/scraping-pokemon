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
    """
    Save an image, from a direct URL to the image, to disk. Image type is
    inferred from the URL.

    Parameters
    ----------
    url : str
        Direct URL to image.
    """

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
) -> Coroutine[Any, Any, Awaitable[str]]:
    """
    Generates a unique hash.

    Parameters
    ----------
    value : Union[str, int, float, list, tuple, set]
        Object to generate hash from.
    kind : Literal[&quot;sha-1&quot;, &quot;sha-256&quot;], optional
        Hashing algorithm, by default "sha-1"

    Returns
    -------
    Coroutine[Any, Any, Awaitable[str]]
        Generated hash.

    Raises
    ------
    ValueError
        If unsupported value type has been provided.
    ValueError
        If unsupported hashing kind has been provided.
    """

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
    """
    Save screenshot of a Playwright Page or Locator element.

    Parameters
    ----------
    element : Union[Locator, Page]
        Playwright Page or Locator to screenshot.
    filename : str
        Filename of the saved image.
    img_type : Literal[&quot;jpg&quot;, &quot;png&quot;]
        Image format.
    full_page : bool, optional
        Whether or not to screenshot the full page, by default False
    """

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
    """
    Dump object to JSON file.

    Parameters
    ----------
    obj : Any
        Serializable object to dump.
    filename : str
        Filename of the dump.
    sort : bool, optional
        Whether or not to sort the dumped JSON by key, by default False
    """

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
    """
    Cleans the provided text from unicode weirdness. The provided text is
    assumed to have been processed by unicodedata.normalize first.

    Parameters
    ----------
    text : str
        Text containing unicode weirdness.

    Returns
    -------
    str
        Cleaned text
    """

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
    """
    Navigates the provided browser, or page, to the provided url.

    Parameters
    ----------
    url : str
        URL to navigate to.
    browser : Optional[Browser], optional
        Playwright Browser instance, by default None
    page : Optional[Page], optional
        Playwright Page instance, by default None

    Returns
    -------
    Coroutine[Any, Any, Awaitable[Page]]
        Playwright Page object of the navigation result.

    Raises
    ------
    TypeError
        If neither the page nor browser arguments have been provided.
    """

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
    """
    Dumps a recording of the internal rich console to vector (svg), or HTML
    format.

    Parameters
    ----------
    title : str
        Title of the file.
    type : Literal[&quot;svg&quot;, &quot;html&quot;]
        File type of ump.

    Raises
    ------
    ValueError
        If provided type is not supported.
    """

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
    """
    Facilitate teardown procedures for the provided browser object.

    Parameters
    ----------
    browser : Browser
        Playwright Browser instance.
    """

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
    """
    Playwright async API context manager entrypoint.
    """

    async with async_playwright() as backend:
        # Log
        environ.CONSOLE.log("Initiating async browser context...")

        await scraping.main_coroutine(backend)
