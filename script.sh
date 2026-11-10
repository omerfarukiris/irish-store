#!/bin/bash
set -euo pipefail

# Çalıştırma: bash script.sh
# İsteğe bağlı port: bash script.sh 8001
PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

cd "$PROJECT_DIR/novastore"
exec "$PROJECT_DIR/.venv/bin/python" manage.py runserver "$@"
