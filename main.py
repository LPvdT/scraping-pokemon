import asyncio
from sys import stdin
from typing import List, Literal, Optional, TextIO, Tuple
from unicodedata import normalize
from urllib.parse import urljoin

from playwright.async_api import (
    Browser,
    Locator,
    Page,
    Playwright,
    async_playwright,
    expect,
)
from rich.console import Console

import src as source

__all__: List[str] = ["source"]

# Setup
CONSOLE = Console(record=True, tab_size=4)

# Switches
KEEP_ALIVE = False
FIREFOX_PARAMS = dict(headless=False, timeout=5000)

# URL
URL_ROOT = "https://pokemondb.net"
URL_POKEDEX_INDEX = "pokedex"
ENTRYPOINT: str = urljoin(URL_ROOT, URL_POKEDEX_INDEX)


async def navigate(
    url: str,
    browser: Optional[Browser] = None,
    page: Optional[Page] = None,
) -> Page:
    if not page and not browser:
        raise TypeError("Either 'browser' or 'page' must be provided")

    if page:
        await page.goto(url)
    else:
        page = await browser.new_page()
        await page.goto(url)

    # Log
    CONSOLE.rule("[bold]Page title")
    CONSOLE.log(await page.title())

    return page


async def get_pokedex_urls(page: Page) -> List[str]:
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
        db_urls_pokedex.append(pokedex)

    return db_urls_pokedex


async def get_generation_urls(
    page: Page, urls_pokedex: List[str]
) -> List[str]:
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
        db_urls_generations.append(urljoin(urls_pokedex[0], href))

    return db_urls_generations


async def get_pokedex_cards(
    page, urls_pokedex
) -> Tuple[List[dict], List[dict]]:
    # Storage
    db_pokedex_card_image: List[dict] = list()
    db_pokedex_card_data: List[dict] = list()

    # HACK: Limit for debugging
    limit_pokedex = 1

    if limit_pokedex > 0:
        urls_pokedex = urls_pokedex[:limit_pokedex]

        CONSOLE.rule(
            f"[bold red]LIMIT[/bold red]: 'urls_pokedex' - {limit_pokedex}"
        )

    for url in urls_pokedex:
        # Follow Pokédex URL
        page = await navigate(url=url, page=page)

        # Pokémon grid
        locator_card_container: Locator = page.locator(
            ".infocard-list"
        ).nth(0)
        await expect(locator_card_container).to_be_visible()

        # Get card data
        locator_card_img_data: Locator = locator_card_container.locator(
            ".infocard-lg-img"
        )
        locator_card_data: Locator = locator_card_container.locator(
            ".infocard-lg-data"
        )

        card_img_data_all = await locator_card_img_data.all()
        card_data_all = await locator_card_data.all()

        # HACK: Limit for debugging
        limit_cards = 1

        if limit_cards > 0:
            limit_cards = int(limit_cards * 5)
            card_img_data_all = card_img_data_all[:limit_cards]
            card_data_all = card_data_all[:limit_cards]

            CONSOLE.rule(
                f"[bold red]LIMIT[/bold red]: 'urls_pokedex' - {limit_cards}"
            )

        for card_image, card_data in zip(
            card_img_data_all, card_data_all
        ):
            # Storage
            db_card_image = dict(
                url=list(), img_src=list(), img_alt=list()
            )
            db_card_data = dict(number=list(), types=list())

            # Extract card image data
            url: str = urljoin(
                URL_ROOT,
                await card_image.get_by_role("link").get_attribute(
                    "href"
                ),
            )
            img_src: str | None = await card_image.get_by_role(
                "img"
            ).get_attribute("src")
            img_alt: str | None = await card_image.get_by_role(
                "img"
            ).get_attribute("alt")

            # Add to db
            db_card_image["url"].append(url)
            db_card_image["img_src"].append(img_src)
            db_card_image["img_alt"].append(img_alt)

            # HACK
            CONSOLE.rule("[bold]card_image")
            CONSOLE.log("[bold]URL:", url)
            CONSOLE.log("[bold]IMG SRC:", img_src)
            CONSOLE.log("[bold]IMG ALT:", img_alt)

            # Extract card data
            number: str = await card_data.locator(
                "small"
            ).first.inner_text()

            locator_types: Locator = (
                card_data.locator("small").nth(1).get_by_role("link")
            )

            types: list(str) = list()

            for t in await locator_types.all():
                types.append(await t.inner_text())

            # Add to db
            db_card_data["number"].append(number)
            db_card_data["types"].append(types)

            # HACK
            CONSOLE.rule("[bold]card_data")
            CONSOLE.log("[bold]NUMBER:", number)
            CONSOLE.log("[bold]TYPES:", "; ".join(types))

            # Append to db
            db_pokedex_card_image.append(db_card_image)
            db_pokedex_card_data.append(db_card_data)

    # HACK
    CONSOLE.rule("[bold]db_pokedex_card_image")
    CONSOLE.log(db_pokedex_card_image)

    CONSOLE.rule("[bold]db_pokedex_card_data")
    CONSOLE.log(db_pokedex_card_data)

    return db_pokedex_card_image, db_pokedex_card_data


async def dump_console_recording(
    console: Console, title: str, type: Literal["svg", "html"]
) -> None:
    params = dict(
        path=f"./data/static/logs/{title}.svg",
        title=title.title(),
    )

    if type == "svg":
        console.save_svg(**params)
    elif type == "html":
        console.save_html(
            **params.update(
                path=params["path"].replace(".svg", ".html")
            )
        )
    else:
        raise ValueError(f"'{type}' is not a valid argument for type")


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


async def main_coroutine(backend: Playwright) -> None:
    # Launch browser and navigate
    browser: Browser = await backend.firefox.launch(**FIREFOX_PARAMS)
    CONSOLE.log("Browser started! 😸")

    # Follow entrypoint URL
    page: Page = await navigate(url=ENTRYPOINT, browser=browser)

    # Show title
    await dump_console_recording(
        CONSOLE, title="root_title", type="svg"
    )

    # Get Pokédex URLs
    urls_pokedex: List[str] = await get_pokedex_urls(page)
    await dump_console_recording(
        CONSOLE, title="urls_pokedex", type="svg"
    )

    # Get generation URLs
    _: List[str] = await get_generation_urls(page, urls_pokedex)
    await dump_console_recording(
        CONSOLE, title="urls_generations", type="svg"
    )

    # Data Pokédex cards
    (
        data_pokedex_cards_img,
        data_pokedex_cards_data,
    ) = await get_pokedex_cards(page, urls_pokedex)

    # TODO: Refactor to coroutine function
    for url_pokemon in [card["url"] for card in data_pokedex_cards_img]:
        # HACK
        CONSOLE.rule("[bold]url_pokemon")
        CONSOLE.log(url_pokemon[0])

        # Navigate to Pokémon detail page
        page = await navigate(url=url_pokemon[0], page=page)

        # Fetch description
        locator_description: Locator = (
            page.locator("main").locator("p").first
        )
        description: str = await locator_description.inner_text()

        # HACK
        CONSOLE.rule("[bold]Description")
        CONSOLE.log(description)

        ################
        # Pokédex data #
        ################
        db_pokedex_data = dict(
            national_no=list(),
            type=list(),
            species=list(),
            height=list(),
            weight=list(),
            abilities=list(),
            local_no=list(),
        )

        # Extract
        locator_pokedex_data: Locator = page.locator(
            ".vitals-table"
        ).nth(0)
        locator_pokedex_data_row: Locator = (
            locator_pokedex_data.get_by_role("row")
        )

        array_pokedex_data: List[
            str
        ] = await locator_pokedex_data_row.all_inner_texts()

        # Parse
        _, _national_no_data = array_pokedex_data[0].strip().split("\t")
        _national_no_data = normalize("NFKC", _national_no_data)

        _, _type_data = array_pokedex_data[1].strip().split("\t")
        _type_data = normalize("NFKC", _type_data)

        _, _species_data = array_pokedex_data[2].strip().split("\t")
        _species_data = normalize("NFKC", _species_data)

        _, _height_data = array_pokedex_data[3].strip().split("\t")
        _height_data = normalize("NFKC", _height_data)

        _, _weight_data = array_pokedex_data[4].strip().split("\t")
        _weight_data = normalize("NFKC", _weight_data)

        _, _abilities_data = array_pokedex_data[5].strip().split("\t")
        _abilities_data = normalize("NFKC", _abilities_data).split("\n")

        _, _local_no_data = array_pokedex_data[6].strip().split("\t")
        _local_no_data = normalize("NFKC", _local_no_data).split("\n")

        # Store
        db_pokedex_data["national_no"].append(_national_no_data)
        db_pokedex_data["type"].append(_type_data)
        db_pokedex_data["species"].append(_species_data)
        db_pokedex_data["height"].append(_height_data)
        db_pokedex_data["weight"].append(_weight_data)
        db_pokedex_data["abilities"].append(_abilities_data)
        db_pokedex_data["local_no"].append(_local_no_data)

        # HACK
        CONSOLE.rule("[bold]db_pokedex_data")
        CONSOLE.log(db_pokedex_data)

        ############
        # Training #
        ############
        db_training = dict(
            ev_yield=list(),
            catch_rate=list(),
            base_friendship=list(),
            base_exp=list(),
            growth_rate=list(),
        )

        # Extract
        locator_training = page.locator(".vitals-table").nth(1)
        locator_training_row = locator_training.get_by_role("row")

        array_training: List[
            str
        ] = await locator_training_row.all_inner_texts()

        # Parse
        _, _ev_yield_data = array_training[0].strip().split("\t")
        _ev_yield_data = normalize("NFKC", _ev_yield_data)

        _, _catch_rate_data = array_training[1].strip().split("\t")
        _catch_rate_data = normalize("NFKC", _catch_rate_data)

        _, _base_friendship_data = array_training[2].strip().split("\t")
        _base_friendship_data = normalize("NFKC", _base_friendship_data)

        _, _base_exp_data = array_training[3].strip().split("\t")
        _base_exp_data = normalize("NFKC", _base_exp_data)

        _, _growth_rate_data = array_training[4].strip().split("\t")
        _growth_rate_data = normalize("NFKC", _growth_rate_data)

        # Store
        db_training["ev_yield"].append(_ev_yield_data)
        db_training["catch_rate"].append(_catch_rate_data)
        db_training["base_friendship"].append(_base_friendship_data)
        db_training["base_exp"].append(_base_exp_data)
        db_training["growth_rate"].append(_growth_rate_data)

        # HACK
        CONSOLE.rule("[bold]db_training")
        CONSOLE.log(db_training)

        ############
        # Breeding #
        ############
        db_breeding = dict(
            egg_groups=list(), gender=list(), egg_cycles=list()
        )

        # Extract
        locator_breeding = page.locator(".vitals-table").nth(2)
        locator_breeding_row = locator_breeding.get_by_role("row")

        array_breeding: List[
            str
        ] = await locator_breeding_row.all_inner_texts()

        # Parse
        _, _egg_groups_data = array_breeding[0].strip().split("\t")
        _egg_groups_data = normalize("NFKC", _egg_groups_data).split(
            ","
        )

        _, _gender_data = array_breeding[1].strip().split("\t")
        _gender_data = normalize("NFKC", _gender_data)

        _, _egg_cycles_data = array_breeding[2].strip().split("\t")
        _egg_cycles_data = normalize("NFKC", _egg_cycles_data)

        # Store
        db_breeding["egg_groups"].append(_egg_groups_data)
        db_breeding["gender"].append(_gender_data)
        db_breeding["egg_cycles"].append(_egg_cycles_data)

        # HACK
        CONSOLE.rule("[bold]db_breeding")
        CONSOLE.log(db_breeding)

        ##############
        # Base stats #
        ##############
        db_base_stats = dict(
            hp=dict(),
            attack=dict(),
            defense=dict(),
            special_attack=dict(),
            special_defense=dict(),
            speed=dict(),
        )
        db_base_stats_record_keys = ["base", "min", "max"]

        # Extract
        locator_base_stats = page.locator(".vitals-table").nth(3)
        locator_base_stats_row = locator_base_stats.get_by_role("row")

        array_base_stats = (
            await locator_base_stats_row.all_inner_texts()
        )

        # Parse
        _hp_data = array_base_stats[0].strip().split("\t")
        _hp_data.remove("\n")
        _hp_data.pop(0)

        _attack_data = array_base_stats[1].strip().split("\t")
        _attack_data.remove("\n")
        _attack_data.pop(0)

        _defense_data = array_base_stats[2].strip().split("\t")
        _defense_data.remove("\n")
        _defense_data.pop(0)

        _special_attack_data = array_base_stats[3].strip().split("\t")
        _special_attack_data.remove("\n")
        _special_attack_data.pop(0)

        _special_defense_data = array_base_stats[4].strip().split("\t")
        _special_defense_data.remove("\n")
        _special_defense_data.pop(0)

        _speed_data = array_base_stats[5].strip().split("\t")
        _speed_data.remove("\n")
        _speed_data.pop(0)

        # Store
        db_base_stats["hp"] = {
            key: int(value)
            for (key, value) in zip(db_base_stats_record_keys, _hp_data)
        }
        db_base_stats["attack"] = {
            key: int(value)
            for (key, value) in zip(
                db_base_stats_record_keys, _attack_data
            )
        }
        db_base_stats["defense"] = {
            key: int(value)
            for (key, value) in zip(
                db_base_stats_record_keys, _defense_data
            )
        }
        db_base_stats["special_attack"] = {
            key: int(value)
            for (key, value) in zip(
                db_base_stats_record_keys, _special_attack_data
            )
        }
        db_base_stats["special_defense"] = {
            key: int(value)
            for (key, value) in zip(
                db_base_stats_record_keys, _special_defense_data
            )
        }
        db_base_stats["speed"] = {
            key: int(value)
            for (key, value) in zip(
                db_base_stats_record_keys, _speed_data
            )
        }

        # HACK
        CONSOLE.rule("[bold]db_base_stats")
        CONSOLE.log(db_base_stats)

        ###################
        # Pokédex entries #
        ###################
        db_pokedex_entries = dict(game=list(), entry=list())

        # Extract
        locator_pokedex_entries = page.locator(".vitals-table").nth(4)
        locator_pokedex_entries_row = (
            locator_pokedex_entries.get_by_role("row")
        )

        array_pokedex_entries: List[
            str
        ] = await locator_pokedex_entries_row.all_inner_texts()

        for record in array_pokedex_entries:
            # Parse
            _game_data, _entry_data = record.strip().split("\t")
            _game_data, _entry_data = normalize(
                "NFKC", _game_data
            ), normalize("NFKC", _entry_data)
            _game_data = _game_data.split("\n")

            # Store
            db_pokedex_entries["game"].append(_game_data)
            db_pokedex_entries["entry"].append(_entry_data)

        # HACK
        CONSOLE.rule("[bold]db_pokedex_entries")
        CONSOLE.log(db_pokedex_entries)

        #################
        # Where to find #
        #################
        db_where_to_find = dict(game=list(), location=list())

        # Extract
        locator_where_to_find = page.locator(".vitals-table").nth(5)
        locator_where_to_find_row = locator_where_to_find.get_by_role(
            "row"
        )

        array_where_to_find: List[
            str
        ] = await locator_where_to_find_row.all_inner_texts()

        for record in array_where_to_find:
            # Parse
            _game_data, _location_data = record.strip().split("\t")
            _game_data, _location_data = normalize(
                "NFKC", _game_data
            ), normalize("NFKC", _location_data)
            _game_data = _game_data.split("\n")

            # Store
            db_where_to_find["game"].append(_game_data)
            db_where_to_find["location"].append(_location_data)

        # HACK
        CONSOLE.rule("[bold]db_where_to_find")
        CONSOLE.log(db_where_to_find)

        ###################
        # Other languages #
        ###################
        db_other_languages = dict(language=list(), name=list())

        # Extract
        locator_other_languages = page.locator(".vitals-table").nth(6)
        locator_other_languages_row = (
            locator_other_languages.get_by_role("row")
        )

        array_other_languages: List[
            str
        ] = await locator_other_languages_row.all_inner_texts()

        for record in array_other_languages:
            # Parse
            _language_data, _name_data = record.strip().split("\t")
            _language_data, _name_data = normalize(
                "NFKC", _language_data
            ), normalize("NFKC", _name_data)
            _language_data = _language_data.split("\n")

            # Store
            db_other_languages["language"].append(_language_data)
            db_other_languages["name"].append(_name_data)

        # HACK
        CONSOLE.rule("[bold]db_other_languages")
        CONSOLE.log(db_other_languages)

    # Teardown
    await teardown(browser)


async def entrypoint() -> None:
    async with async_playwright() as backend:
        await main_coroutine(backend)


if __name__ == "__main__":
    asyncio.run(entrypoint())
