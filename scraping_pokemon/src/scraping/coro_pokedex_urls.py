from typing import Any, Awaitable, Coroutine, List
from urllib.parse import urljoin

from playwright.async_api import Locator, Page, expect

from scraping_pokemon.src.environ import URL_ROOT

from ..database.db import table_pokedex


async def get_pokedex_urls(
    page: Page,
) -> Coroutine[Any, Any, Awaitable[List[str]]]:
    # Storage
    db_urls_pokedex: List[str] = list()

    # Locate Pokédexes list
    locator_main: Locator = page.get_by_role("main")
    await expect(locator_main).to_be_visible()

    locator_pokedexes: Locator = (
        locator_main.get_by_role("navigation")
        .get_by_role("list")
        .nth(1)
        .get_by_role("listitem")
    )

    # Extract and compile URLs
    for li in await locator_pokedexes.all():
        pokedex: str = urljoin(
            URL_ROOT, await li.get_by_role("link").get_attribute("href")
        )
        # Add to storage
        db_urls_pokedex.append(pokedex)

        # Insert into db
        table_pokedex.insert(dict(pokedex_url=pokedex))

    return db_urls_pokedex
