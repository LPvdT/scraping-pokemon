from src.database.db import db
import pandas as pd
from tinydb import Query


def run() -> None:
    pokemon = Query()

    res = db.table("pokemon").all()

    print(len(res))
    # pd.json_normalize(res)

    res_cards = db.table("cards_img").all()

    print(len(res_cards))
