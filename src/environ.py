from pathlib import Path
from urllib.parse import urljoin

from rich.console import Console

from src.types import FirefoxParams


# Setup
CONSOLE = Console(record=True, tab_size=4)

# Switches
FIREFOX_PARAMS = FirefoxParams(
    headless=False,
)
KEEP_ALIVE = False
LIMIT_POKEDEX = 1
LIMIT_CARDS = 5

# URL
URL_ROOT = "https://pokemondb.net"
URL_POKEDEX_INDEX = "pokedex"
ENTRYPOINT: str = urljoin(URL_ROOT, URL_POKEDEX_INDEX)

# Structure
FOLDERS: list[str] = ["data/static/img", "data/static/logs"]


def create_env() -> None:
    for folder in FOLDERS:
        Path(folder).mkdir(parents=True, exist_ok=True)
