from .src.database.db import db
import pandas as pd


def run() -> None:
    res = db.table("pokemon").all()
    res_cards = db.table("cards_img").all()

    print(len(res))
    print(pd.json_normalize(res).head(25))

    print(len(res_cards))
    print(pd.json_normalize(res_cards).head(25))
