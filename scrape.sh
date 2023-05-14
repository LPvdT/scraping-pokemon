#!/bin/bash

DIRECTORY=${PWD##*/}
DIRECTORY=${DIRECTORY:-/}

if [ "$DIRECTORY" = "scraping-pokemon" ]; then
    # Call scrape script
    poetry run scrape
else
    echo "Please run this script with the repository as working directory."
fi
