#!/bin/bash

DIRECTORY=${PWD##*/}
DIRECTORY=${DIRECTORY:-/}

if [ "$DIRECTORY" = "scraping-pokemon" ]; then
    # Install Poetry
    pip install poetry

    # Ensure vens gets placed in repo directory and respects potential existing
    # vens
    poetry config virtualenvs.in-project true --local

    # Install project
    poetry install

    # Install browser
    poetry run playwright install firefox
else
    echo "Please run this script with the repository as working directory."
fi
