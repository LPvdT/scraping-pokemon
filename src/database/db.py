from pathlib import Path

from BetterJSONStorage import BetterJSONStorage
from tinydb import TinyDB

from src.environ import CONSOLE, TRUNCATE

db = TinyDB(
    Path("./data/db/nosql.db"),
    access_mode="r+",
    storage=BetterJSONStorage,
)

table_pokemon = db.table("pokemon")

if TRUNCATE:
    CONSOLE.log("[bold red]Truncating table...")
    table_pokemon.truncate()
