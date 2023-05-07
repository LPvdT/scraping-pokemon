from typing import List

from peewee import Model, SqliteDatabase

from src.db.models import (
    CardsData,
    CardsImg,
    GenerationUrl,
    PokedexUrl,
    PokemonBase,
    PokemonBaseStats,
    PokemonBreeding,
    PokemonEntry,
    PokemonLanguages,
    PokemonLocation,
    PokemonPokedex,
    PokemonTraining,
)
from src.environ import CREATE, TRUNCATE

db = SqliteDatabase("./data/db/sqlite.db")

models: List[Model] = [
    GenerationUrl,
    PokedexUrl,
    CardsData,
    CardsImg,
    PokemonBase,
    PokemonPokedex,
    PokemonTraining,
    PokemonBreeding,
    PokemonBaseStats,
    PokemonEntry,
    PokemonLocation,
    PokemonLanguages,
]

if CREATE:
    db.create_tables(models)

if TRUNCATE:
    for model in models:
        model.truncate_table()
