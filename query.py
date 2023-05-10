from src.database.db import db
import pandas as pd
from tinydb import Query

pokemon = Query()

res = db.table("pokemon").all()

pd.json_normalize(res)

db.table("cards_img").all()
