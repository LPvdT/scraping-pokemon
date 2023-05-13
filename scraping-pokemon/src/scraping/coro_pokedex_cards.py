from typing import Any, Awaitable, Coroutine, List, Tuple
from urllib.parse import urljoin

from playwright.async_api import Locator, expect

import src.utils as utils
from src.database.db import table_cards_data, table_cards_img
from src.environ import CONSOLE, LIMIT_CARDS, LIMIT_POKEDEX, URL_ROOT


async def get_pokedex_cards(
    page, urls_pokedex
) -> Coroutine[Any, Any, Awaitable[Tuple[List[dict], List[dict]]]]:
    # Storage
    db_pokedex_card_image: List[dict] = list()
    db_pokedex_card_data: List[dict] = list()

    # Pokédex limit
    if LIMIT_POKEDEX > 0:
        urls_pokedex = urls_pokedex[:LIMIT_POKEDEX]

        CONSOLE.log(
            f"[bold red]LIMIT[/bold red]: 'urls_pokedex' - {LIMIT_POKEDEX} records"
        )

    for url in urls_pokedex:
        # Follow Pokédex URL
        page = await utils.navigate(url=url, page=page)

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

        # Card limit
        if LIMIT_CARDS > 0:
            card_img_data_all = card_img_data_all[:LIMIT_CARDS]
            card_data_all = card_data_all[:LIMIT_CARDS]

            CONSOLE.log(
                f"[bold red]LIMIT[/bold red]: 'urls_pokedex' - {LIMIT_CARDS} records"
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

            # Add to storage
            db_pokedex_card_image.append(db_card_image)
            db_pokedex_card_data.append(db_card_data)

            # Insert into db
            table_cards_img.insert(dict(card_image=db_card_image))
            table_cards_data.insert(dict(card_data=db_card_data))

    return db_pokedex_card_image, db_pokedex_card_data
