#!/bin/bash
# import.sh — Aplica la configuración del repo a una instancia de OpenWebUI.
# Uso: bash scripts/import.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  OpenWebUI Config — Import"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Cargar .env si existe
if [ -f "$ROOT_DIR/.env" ]; then
    export $(grep -v '^#' "$ROOT_DIR/.env" | xargs)
    echo "✓ .env cargado"
fi

# Verificar vars de entorno
if [ -z "$OPENWEBUI_URL" ]; then
    echo "❌ OPENWEBUI_URL no está configurado"
    exit 1
fi

if [ -z "$OPENWEBUI_TOKEN" ]; then
    echo "❌ OPENWEBUI_TOKEN no está configurado"
    exit 1
fi

# Verificar dependencias Python
python3 -c "import requests" 2>/dev/null || pip install requests --quiet
python3 -c "import dotenv" 2>/dev/null || pip install python-dotenv --quiet

echo "→ Destino: $OPENWEBUI_URL"
echo ""

python3 "$SCRIPT_DIR/openwebui_api.py" import
