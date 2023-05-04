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

    # Get Pokédex URLs
    urls_pokedex: List[str] = await get_pokedex_urls(page)

    # Get generation URLs
    data_generation_urls = await get_generation_urls(page, urls_pokedex)

    await utils.save_json(data_generation_urls, "data_generation_urls")

    # Data Pokédex cards
    (
        data_pokedex_cards_img,
        data_pokedex_cards_data,
    ) = await get_pokedex_cards(page, urls_pokedex)

    await utils.save_json(
        data_pokedex_cards_img, "data_pokedex_cards_img"
    )

    await utils.save_json(
        data_pokedex_cards_data, "data_pokedex_cards_data"
    )

    # Get Pokémon details
    data_pokemon_details = await get_pokemon_details(
        page, data_pokedex_cards_img
    )

    await utils.save_json(data_pokemon_details, "data_pokemon_details")

    for _type in ["svg", "html"]:
        await utils.dump_console_recording(
            console=CONSOLE, title="recording", type=_type
        )

    # Teardown
    await utils.teardown(browser)
