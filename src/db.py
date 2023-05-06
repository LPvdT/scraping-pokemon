from tinydb import TinyDB

db = TinyDB("./data/db")

table_pokemon = db.table("pokemon")
