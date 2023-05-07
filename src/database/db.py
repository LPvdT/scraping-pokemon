from tinydb import TinyDB

from src.environ import TRUNCATE, CONSOLE

db = TinyDB("./data/db/nosql.db")

table_pokemon = db.table("pokemon")

if TRUNCATE:
    CONSOLE.log("[bold red]Truncating table...")
    table_pokemon.truncate()
