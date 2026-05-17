#!/bin/bash
# export.sh — Exporta los agentes de OpenWebUI al repo.
# Útil cuando editás desde la UI y querés versionar los cambios.
# Uso: bash scripts/export.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  OpenWebUI Config — Export"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "$ROOT_DIR/.env" ]; then
    export $(grep -v '^#' "$ROOT_DIR/.env" | xargs)
    echo "✓ .env cargado"
fi

if [ -z "$OPENWEBUI_URL" ] || [ -z "$OPENWEBUI_TOKEN" ]; then
    echo "❌ Configurá OPENWEBUI_URL y OPENWEBUI_TOKEN en .env"
    exit 1
fi

python3 -c "import requests" 2>/dev/null || pip install requests --quiet
python3 -c "import dotenv" 2>/dev/null || pip install python-dotenv --quiet

echo "→ Fuente: $OPENWEBUI_URL"
echo ""

python3 "$SCRIPT_DIR/openwebui_api.py" export

echo ""
echo "Revisá los cambios:"
echo "  git diff agents/"
echo ""
echo "Para commitear:"
echo "  git add -A && git commit -m 'chore: sync agents from UI'"
