#!/bin/bash
set -eu

python3 -m venv .venv
source .venv/bin/activate
poetry install

ancs4linux-advertising --help
ancs4linux-ctl --help
ancs4linux-desktop-integration --help
ancs4linux-observer --help

black --check ancs4linux
isort --check ancs4linux
autoflake --check --remove-unused-variables --remove-all-unused-imports -r ancs4linux
mypy --namespace-packages -p ancs4linux
