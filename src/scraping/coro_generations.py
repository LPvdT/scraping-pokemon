from typing import Any, Awaitable, Coroutine, List
from urllib.parse import urljoin

from playwright.async_api import Locator, Page, expect

from src.database.db import AsyncDatabaseInterFace


async def get_generation_urls(
    page: Page, urls_pokedex: List[str]
) -> Coroutine[Any, Any, Awaitable[List[str]]]:
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

        # Append to storage
        db_urls_generations.append(record)

    # Insert into database
    AsyncDatabaseInterFace.insert(
        "generations", dict(generation_urls=db_urls_generations)
    )

    return db_urls_generations
