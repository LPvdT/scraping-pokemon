from typing import Any, Awaitable, Coroutine, List
from urllib.parse import urljoin

from playwright.async_api import Locator, Page, expect

from src.database.db import AsyncDatabaseInterFace
from src.environ import URL_ROOT


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
    await AsyncDatabaseInterFace.insert(
        "pokedex", dict(pokedex_urls=pokedex)
    )

    return db_urls_pokedex
