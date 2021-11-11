#!/bin/bash
set -eu
set -x

ancs4linux-server &
pid1=$!
ancs4linux-desktop-integration &
pid2=$!

$SHELL

kill -INT $pid2 $pid1
wait $pid2
wait $pid1
