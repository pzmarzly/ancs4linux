#!/bin/bash
set -eu

uv sync

uv run ancs4linux-advertising --help
uv run ancs4linux-ctl --help
uv run ancs4linux-desktop-integration --help
uv run ancs4linux-observer --help

uv run black --check ancs4linux
uv run isort --check ancs4linux
uv run autoflake --check --remove-unused-variables --remove-all-unused-imports -r ancs4linux
uv run mypy --namespace-packages -p ancs4linux
