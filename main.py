import asyncio
from datetime import datetime
from typing import List, Optional
from urllib.parse import urljoin

from playwright.async_api import (
    Browser,
    Page,
    Playwright,
    async_playwright,
    expect,
)
from rich.console import Console

import src as source

# Setup
__all__ = ["source"]
CONSOLE = Console(record=True)

# Globals
URL_ROOT = "https://pokemondb.net"
URL_POKEDEX_INDEX = "pokedex"
ENTRYPOINT = urljoin(URL_ROOT, URL_POKEDEX_INDEX)


async def navigate(
    url: str, browser: Optional[Browser] = None, page: Optional[Page] = None
) -> Page:
    if page:
        await page.goto(url)
    else:
        page: Page = await browser.new_page()
        await page.goto(url)

    return page


async def get_pokedex_urls(page: Page) -> List[str]:
    urls_pokedex: List[str] = list()

    # Locate Pokédexes list
    main = page.get_by_role("main")
    await expect(main).to_be_visible()

    pokedexes = (
        page.get_by_role("main")
        .get_by_role("navigation")
        .get_by_role("list")
        .nth(1)
        .get_by_role("listitem")
    )

    # Extract URLs
    for li in await pokedexes.all():
        pokedex = urljoin(
            URL_ROOT, await li.get_by_role("link").get_attribute("href")
        )
        urls_pokedex.append(pokedex)

    return urls_pokedex


async def dump_console_recording(
    console: Console, title: Optional[str] = None
) -> None:
    console.save_svg(
        path=f"./data/static/logs/{title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.svg",
        title=title.title(),
    )


async def teardown(browser: Browser):
    await browser.close()


async def main_routine(backend: Playwright):
    # Launch browser and navigate
    browser = await backend.firefox.launch(headless=False, timeout=5000)
    page = await navigate(url=ENTRYPOINT, browser=browser)

    # Show title
    CONSOLE.log(await page.title())
    await dump_console_recording(CONSOLE, title="root_title")

    # Get Pokédex URLs
    urls_pokedex = await get_pokedex_urls(page)
    CONSOLE.log(urls_pokedex)
    await dump_console_recording(CONSOLE, title="urls_pokedex")

    # Follow Pokédex URLs
    page = await navigate(url=urls_pokedex[0], page=page)

    # Teardown
    await teardown(browser)


async def entrypoint():
    async with async_playwright() as backend:
        await main_routine(backend)


if __name__ == "__main__":
    asyncio.run(entrypoint())
