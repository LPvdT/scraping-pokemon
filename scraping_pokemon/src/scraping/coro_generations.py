from typing import Any, Awaitable, Coroutine, List
from urllib.parse import urljoin

from playwright.async_api import Locator, Page, expect

from ..database.db import table_generations
from ..environ import CONSOLE


async def get_generation_urls(
    page: Page, urls_pokedex: List[str]
) -> Coroutine[Any, Any, Awaitable[List[str]]]:
    """
    Coroutine for scraping the generation URLs.

    Parameters
    ----------
    page : Page
        Playwright Page instance.
    urls_pokedex : List[str]
        List containing Pokédex target URLs.

    Returns
    -------
    Coroutine[Any, Any, Awaitable[List[str]]]
        List containing generation URLs.
    """

    # Log
    CONSOLE.log("Scraping [b]generation URL[/b] data...")

    # Storage
    db_urls_generations: List[str] = list()

    # Locate generations
    locator_main: Locator = page.get_by_role("main")
    await expect(locator_main).to_be_visible()

    locator_links: Locator = locator_main.get_by_role(
        "list"
    ).get_by_role("link")

    # Extract and compile URLs
    for a in await locator_links.all():
        href: str | None = await a.get_attribute("href")
        record = urljoin(urls_pokedex[0], href)

        # Add to storage
        db_urls_generations.append(record)

        # Insert into db
        table_generations.insert(dict(generation_url=record))

    return db_urls_generations
