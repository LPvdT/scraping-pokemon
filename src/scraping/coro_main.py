from typing import Any, Awaitable, Coroutine, List

from playwright.async_api import Browser, Page, Playwright

import src.utils as utils
from src.environ import CONSOLE, ENTRYPOINT, FIREFOX_PARAMS
from src.scraping.coro_generations import get_generation_urls
from src.scraping.coro_pokedex_cards import get_pokedex_cards
from src.scraping.coro_pokedex_urls import get_pokedex_urls
from src.scraping.coro_pokemon_details import get_pokemon_details


async def main_coroutine(
    backend: Playwright,
) -> Coroutine[Any, Any, Awaitable[None]]:
    # Launch browser and navigate
    browser: Browser = await backend.firefox.launch(**FIREFOX_PARAMS)
    CONSOLE.log("Browser started! 😸")

    # Follow entrypoint URL
    page: Page = await utils.navigate(url=ENTRYPOINT, browser=browser)

    # Show title
    await utils.dump_console_recording(
        CONSOLE, title="root_title", type="svg"
    )

    # Get Pokédex URLs
    urls_pokedex: List[str] = await get_pokedex_urls(page)
    await utils.dump_console_recording(
        CONSOLE, title="urls_pokedex", type="svg"
    )

    # Get generation URLs
    _: List[str] = await get_generation_urls(page, urls_pokedex)
    await utils.dump_console_recording(
        CONSOLE, title="urls_generations", type="svg"
    )

    # Data Pokédex cards
    (
        data_pokedex_cards_img,
        data_pokedex_cards_data,
    ) = await get_pokedex_cards(page, urls_pokedex)

    # Get Pokémon details
    # TODO: Return shit from the coroutine
    await get_pokemon_details(page, data_pokedex_cards_img)

    # Teardown
    await utils.teardown(browser)
