from peewee import (
    AutoField,
    ForeignKeyField,
    IntegerField,
    Model,
    TextField,
)

from src.db import db


class BaseModel(Model):
    class Meta:
        database = db


class GenerationUrl(BaseModel):
    generation_id = AutoField()
    url = TextField(null=False, unique=True)


class PokedexUrl(BaseModel):
    pokedex_id = AutoField()
    url = TextField(null=False, unique=True)


class CardsData(BaseModel):
    cards_data_id = AutoField()
    number = TextField()
    types = TextField()


class CardsImg(BaseModel):
    cards_img_id = AutoField()
    url = TextField()
    img_url = TextField()
    img_alt = TextField()


class PokemonBase(BaseModel):
    pokemon_base_id = AutoField()
    pokemon_key = TextField()
    pokemon_description = TextField()


class PokemonPokedex(BaseModel):
    pokemon_pokedex_id = AutoField()
    national_no = TextField()
    types = TextField()
    species = TextField()
    height = TextField()
    weight = TextField()
    abilities = TextField()
    local_no = TextField()

    base_pokemon = ForeignKeyField(PokemonBase, backref="pokedex")


class PokemonTraining(BaseModel):
    pokemon_training_id = AutoField()

    ev_yield = TextField()
    catch_rate = TextField()
    base_friendship = TextField()
    base_exp = TextField()
    growth_rate = TextField()

    base_pokemon = ForeignKeyField(PokemonBase, backref="training")


class PokemonBreeding(BaseModel):
    pokemon_breeding_id = AutoField()

    egg_groups = TextField()
    gender = TextField()
    egg_cycles = TextField()

    base_pokemon = ForeignKeyField(PokemonBase, backref="breeding")


class PokemonBaseStats(BaseModel):
    pokemon_base_stats_id = AutoField()

    hp_base = IntegerField()
    hp_min = IntegerField()
    hp_max = IntegerField()

    attack_base = IntegerField()
    attack_min = IntegerField()
    attack_max = IntegerField()

    defense_base = IntegerField()
    defense_min = IntegerField()
    defense_min = IntegerField()

    special_attack_base = IntegerField()
    special_attack_min = IntegerField()
    special_attack_max = IntegerField()

    special_defense_base = IntegerField()
    special_defense_min = IntegerField()
    special_defense_max = IntegerField()

    speed_base = IntegerField()
    speed_min = IntegerField()
    speed_max = IntegerField()

    base_pokemon = ForeignKeyField(PokemonBase, backref="base_stats")


class PokemonEntry(BaseModel):
    pokemon_entry_id = AutoField()

    game = TextField()
    entry = TextField()

    base_pokemon = ForeignKeyField(PokemonBase, backref="entry")


class PokemonLocation(BaseModel):
    pokemon_location_id = AutoField()

    game = TextField()
    location = TextField()

    base_pokemon = ForeignKeyField(PokemonBase, backref="location")


class PokemonLanguages(BaseModel):
    pokemon_language_id = AutoField()

    language = TextField()
    name = TextField()

    base_pokemon = ForeignKeyField(PokemonBase, backref="language")
