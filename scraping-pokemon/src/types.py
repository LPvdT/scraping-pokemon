from pathlib import Path
from typing import Literal, TypedDict, Union


class FirefoxParams(TypedDict):
    headless: Literal[True, False]
    timeout: Union[float, None]
    slow_mo: Union[float, None]
    downloads_path: Union[str, Path, None]
    traces_dir: Union[str, Path, None]
