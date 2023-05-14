#!/bin/bash

DIRECTORY=${PWD##*/}
DIRECTORY=${DIRECTORY:-/}

if [ "$DIRECTORY" = "scraping-pokemon" ]; then
    # Call query script
    poetry run query
else
    echo "Please run this script with the repository as working directory."
fi
