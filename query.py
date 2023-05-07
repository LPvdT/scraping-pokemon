from src.database.db import db
from tinydb import Query

pokemon = Query()
db.table("pokemon").search(pokemon.name == "Bulbasaur")
