from typing import Any, Awaitable, Coroutine, List
from unicodedata import normalize

from playwright.async_api import Locator, Page

import src.utils as utils


async def get_pokemon_details(
    page: Page, data_pokedex_cards_img: List[dict]
) -> Coroutine[Any, Any, Awaitable[dict]]:
    # Storage
    names = list()
    descriptions = list()
    pokedex_data = list()
    training = list()
    breeding = list()
    base_stats = list()
    pokedex_entries = list()
    where_to_find = list()
    other_languages = list()

    for url_pokemon in [card["url"] for card in data_pokedex_cards_img]:
        # Navigate to Pokémon detail page
        page = await utils.navigate(url=url_pokemon[0], page=page)

        # Fetch name
        locator_name = page.locator("main").get_by_role("heading").first
        _name = await locator_name.inner_text()

        name = normalize("NFKC", _name)

        # Screenshot page
        await utils.save_screenshot(
            element=page, filename=name, img_type="png", full_page=True
        )

        # Fetch description
        locator_description: Locator = (
            page.locator("main").locator("p").first
        )
        _description: str = await locator_description.inner_text()

        description = normalize("NFKC", _description)

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

        # Add iteration to storage
        names.append(name)
        descriptions.append(description)
        pokedex_data.append(db_pokedex_data)
        training.append(db_training)
        breeding.append(db_breeding)
        base_stats.append(db_base_stats)
        pokedex_entries.append(db_pokedex_entries)
        where_to_find.append(db_where_to_find)
        other_languages.append(db_other_languages)

    return {
        "name": name,
        "description": descriptions,
        "pokedex_data": pokedex_data,
        "training": training,
        "breeding": breeding,
        "base_stats": base_stats,
        "pokedex_entries": pokedex_entries,
        "where_to_find": where_to_find,
        "other_languages": other_languages,
    }
