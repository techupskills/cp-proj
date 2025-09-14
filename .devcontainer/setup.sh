#!/usr/bin/env bash
set -euo pipefail
sudo apt-get update -y
if ! command -v curl >/dev/null 2>&1; then sudo apt-get install -y curl; fi
if ! command -v ollama >/dev/null 2>&1; then curl -fsSL https://ollama.com/install.sh | sh; fi
pip install --upgrade pip
pip install -r requirements.txt
