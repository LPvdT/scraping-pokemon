from pathlib import Path

from BetterJSONStorage import BetterJSONStorage
from tinydb import TinyDB

from ..environ import CONSOLE, TRUNCATE

db = TinyDB(
    Path("./data/db/nosql.db"),
    access_mode="r+",
    storage=BetterJSONStorage,
)

table_pokedex = db.table("pokedex")
table_generations = db.table("generations")
table_cards_data = db.table("cards_data")
table_cards_img = db.table("cards_img")
table_pokemon = db.table("pokemon")

if TRUNCATE:
    CONSOLE.log("[bold red]Truncating table...")
    table_pokemon.truncate()
