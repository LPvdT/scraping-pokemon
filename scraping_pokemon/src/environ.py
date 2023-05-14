from pathlib import Path
from urllib.parse import urljoin

from rich.console import Console

from .types import FirefoxParams

# Setup
CONSOLE = Console(record=True, tab_size=2)
FIREFOX_PARAMS = FirefoxParams(
    headless=False,
)

# Switches
KEEP_ALIVE: bool = False
PAGE_TIMEOUT: int = 5000
LIMIT_POKEDEX: int = 1
LIMIT_CARDS: int = 0
SCREENSHOT_PAGE: bool = False

# DB
TRUNCATE: bool = False

# URL
URL_ROOT = "https://pokemondb.net"
URL_POKEDEX_INDEX = "pokedex"
ENTRYPOINT = urljoin(URL_ROOT, URL_POKEDEX_INDEX)

# Structure
FOLDERS: list[str] = [
    "data/static/img/screenshots",
    "data/static/img/pokemon",
    "data/static/logs",
    "data/static/out",
    "data/db",
]


def create_env() -> None:
    CONSOLE.log("Creating/asserting folder structure...")

    for folder in FOLDERS:
        Path(folder).mkdir(parents=True, exist_ok=True)
