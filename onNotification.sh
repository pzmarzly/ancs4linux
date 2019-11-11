#!/bin/bash

# $1 - app name
# $2 - package name
# $3 - message
notify-send -t 10000 "$1 ($2)" "$3"
