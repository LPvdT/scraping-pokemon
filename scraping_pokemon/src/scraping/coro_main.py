from typing import Any, Awaitable, Coroutine, List

from playwright.async_api import Browser, Page, Playwright

import scraping_pokemon.src.utils as utils

from ..environ import CONSOLE, ENTRYPOINT, FIREFOX_PARAMS
from .coro_generations import get_generation_urls
from .coro_pokedex_cards import get_pokedex_cards
from .coro_pokedex_urls import get_pokedex_urls
from .coro_pokemon_details import get_pokemon_details


async def main_coroutine(
    backend: Playwright,
) -> Coroutine[Any, Any, Awaitable[None]]:
    # Launch browser and navigate
    CONSOLE.rule("[b]Browser & target[/b]")
    browser: Browser = await backend.firefox.launch(**FIREFOX_PARAMS)
    CONSOLE.log("Browser started! 😸")

    # Follow entrypoint URL
    page: Page = await utils.navigate(url=ENTRYPOINT, browser=browser)
    CONSOLE.log(f"Navigated to target: '{ENTRYPOINT}'")

    # Get Pokédex URLs
    CONSOLE.rule("[b]Pokédex URLs[/b]")
    urls_pokedex: List[str] = await get_pokedex_urls(page)
    await utils.save_json(urls_pokedex, "data_urls_pokedex")
    CONSOLE.log("Scraped and serialized [b]Pokédex URL[/b] data.")

    # Get generation URLs
    CONSOLE.rule("[b]Generation URLs[/b]")
    data_generation_urls = await get_generation_urls(page, urls_pokedex)
    await utils.save_json(data_generation_urls, "data_generation_urls")
    CONSOLE.log("Scraped and serialized [b]generation URL[/b] data.")

    # Data Pokédex cards
    CONSOLE.rule("[b]Pokédex cards[/b]")
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
    CONSOLE.log(
        "Scraped and serialized [b]Pokédex cards image data[/b] and [b]Pokédex cards data[/b]."
    )

    # Get Pokémon details
    CONSOLE.rule("[b]Pokémon details[/b]")
    data_pokemon_details = await get_pokemon_details(
        page, data_pokedex_cards_img
    )
    await utils.save_json(data_pokemon_details, "data_pokemon_details")
    CONSOLE.log("Scraped and serialized [b]Pokémon details data[/b].")

    # Dump console logs
    CONSOLE.rule("[b]Teardown[/b]")

    for _type in ["svg", "html"]:
        await utils.dump_console_recording(
            title="console_log", type=_type
        )

    # Teardown
    await utils.teardown(browser)
