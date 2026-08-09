$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$env:TMP = Join-Path $root 'tmp'
$env:TEMP = Join-Path $root 'tmp'
New-Item -ItemType Directory -Force -Path $env:TMP | Out-Null
uv run pytest @args
