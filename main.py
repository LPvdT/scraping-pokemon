import asyncio
from sys import stdin
from typing import Optional, TextIO
from urllib.parse import urljoin

from playwright.async_api import (
    Browser,
    Page,
    Playwright,
    async_playwright,
    expect,
    Locator,
)
from rich.console import Console

import src as source

__all__: list[str] = ["source"]

# Setup
CONSOLE = Console(record=True)

KEEP_ALIVE = False
FIREFOX_PARAMS = dict(headless=False, timeout=5000)

# Globals
URL_ROOT = "https://pokemondb.net"
URL_POKEDEX_INDEX = "pokedex"
ENTRYPOINT: str = urljoin(URL_ROOT, URL_POKEDEX_INDEX)


async def navigate(
    url: str,
    browser: Optional[Browser] = None,
    page: Optional[Page] = None,
) -> Page:
    if page:
        await page.goto(url)
    else:
        page = await browser.new_page()
        await page.goto(url)

    CONSOLE.log("[bold]Title:", await page.title())

    return page


async def get_pokedex_urls(page: Page) -> list[str]:
    urls_pokedex: list[str] = list()

    # Locate Pokédexes list
    main: Locator = page.get_by_role("main")
    await expect(main).to_be_visible()

    pokedexes: Locator = (
        main.get_by_role("navigation")
        .get_by_role("list")
        .nth(1)
        .get_by_role("listitem")
    )

    # Extract and compile URLs
    for li in await pokedexes.all():
        pokedex: str = urljoin(
            URL_ROOT, await li.get_by_role("link").get_attribute("href")
        )
        urls_pokedex.append(pokedex)

    return urls_pokedex


async def get_generation_urls(
    page: Page, urls_pokedex: list[str]
) -> list[str]:
    generations: list[str] = list()

    # Navigate to Pokédexes page
    page = await navigate(url=urls_pokedex[0], page=page)

    # Locate generations
    main: Locator = page.get_by_role("main")
    await expect(main).to_be_visible()

    links: Locator = main.get_by_role("list").get_by_role("link")

    # Extract and compile URLs
    for a in await links.all():
        href: str | None = await a.get_attribute("href")
        generations.append(urljoin(urls_pokedex[0], href))

    return generations


async def dump_console_recording(console: Console, title: str) -> None:
    console.save_svg(
        path=f"./data/static/logs/{title}.svg",
        title=title.title(),
    )


async def teardown(browser: Browser) -> None:
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


async def main_routine(backend: Playwright) -> None:
    # Launch browser and navigate
    browser: Browser = await backend.firefox.launch(**FIREFOX_PARAMS)
    CONSOLE.log("Browser started! 😸")

    # Follow entrypoint URL
    page: Page = await navigate(url=ENTRYPOINT, browser=browser)

    # Show title
    await dump_console_recording(CONSOLE, title="root_title")

    # Get Pokédex URLs
    urls_pokedex: list[str] = await get_pokedex_urls(page)
    await dump_console_recording(CONSOLE, title="urls_pokedex")

    # Follow Pokédex URL
    _: list[str] = await get_generation_urls(page, urls_pokedex)
    await dump_console_recording(CONSOLE, title="urls_generations")

    # Teardown
    await teardown(browser)


async def entrypoint() -> None:
    async with async_playwright() as backend:
        await main_routine(backend)


if __name__ == "__main__":
    asyncio.run(entrypoint())
