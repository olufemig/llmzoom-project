#!/usr/bin/env sh
set -eu

root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
mkdir -p "$root/tmp"
TMP="$root/tmp" TEMP="$root/tmp" uv run pytest "$@"
