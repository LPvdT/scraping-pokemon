from peewee import Model, TextField, AutoField
from src.db import db


class BaseModel(Model):
    class Meta:
        database = db


class Types(BaseModel):
    pokemon_type = TextField()


class GenerationUrl(BaseModel):
    generation_id = AutoField()
    generation_url = TextField(null=False, unique=True)


class PokedexUrl(BaseModel):
    pokedex_id = AutoField()
    pokedex_url = TextField(null=False, unique=True)
