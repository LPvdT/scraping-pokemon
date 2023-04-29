from pathlib import Path

FOLDERS = ["data/static/img", "data/static/logs"]


def create_env() -> None:
    for folder in FOLDERS:
        Path(folder).mkdir(parents=True, exist_ok=True)
