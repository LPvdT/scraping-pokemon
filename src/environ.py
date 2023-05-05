from pathlib import Path
from urllib.parse import urljoin

from rich.console import Console

from src.types import FirefoxParams

# Setup
CONSOLE = Console(record=True, tab_size=4)
FIREFOX_PARAMS = FirefoxParams(
    headless=False,
)

# Switches
KEEP_ALIVE: bool = False
LIMIT_POKEDEX: int = 1
LIMIT_CARDS: int = 5
SCREENSHOT_PAGE: bool = False

# URL
URL_ROOT = "https://pokemondb.net"
URL_POKEDEX_INDEX = "pokedex"
ENTRYPOINT = urljoin(URL_ROOT, URL_POKEDEX_INDEX)

# Structure
FOLDERS: list[str] = [
    "data/static/img",
    "data/static/logs",
    "data/static/out",
]


def create_env() -> None:
    for folder in FOLDERS:
        Path(folder).mkdir(parents=True, exist_ok=True)
