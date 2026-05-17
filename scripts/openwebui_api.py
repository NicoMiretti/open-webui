#!/usr/bin/env python3
"""
openwebui_api.py — CLI para sincronizar agentes entre este repo y OpenWebUI.

Uso:
    python3 scripts/openwebui_api.py import   # repo → OpenWebUI
    python3 scripts/openwebui_api.py export   # OpenWebUI → repo

Variables de entorno requeridas:
    OPENWEBUI_URL    (ej: http://localhost:3000)
    OPENWEBUI_TOKEN  (API key generada en OpenWebUI → Settings → Account → API Keys)
"""

import json
import os
import re
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.environ.get("OPENWEBUI_URL", "http://localhost:3000").rstrip("/")
TOKEN = os.environ.get("OPENWEBUI_TOKEN", "")
AGENTS_DIR = Path(__file__).parent.parent / "agents"

if not TOKEN:
    print("❌ OPENWEBUI_TOKEN no está configurado. Revisá tu .env")
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _slug(name: str) -> str:
    """Convierte un nombre de agente a un ID válido para OpenWebUI."""
    # Eliminar emojis y caracteres no ASCII
    name = re.sub(r'[^\x00-\x7F]+', '', name)
    name = name.strip().lower()
    name = re.sub(r'[^a-z0-9]+', '-', name)
    name = name.strip('-')
    return name


def _get(endpoint: str) -> requests.Response:
    return requests.get(f"{BASE_URL}{endpoint}", headers=HEADERS, timeout=10)


def _post(endpoint: str, payload: dict) -> requests.Response:
    return requests.post(f"{BASE_URL}{endpoint}", headers=HEADERS, json=payload, timeout=10)


def _delete(endpoint: str) -> requests.Response:
    return requests.delete(f"{BASE_URL}{endpoint}", headers=HEADERS, timeout=10)


# ---------------------------------------------------------------------------
# Import: repo → OpenWebUI
# ---------------------------------------------------------------------------

def load_agent(agent_dir: Path) -> dict:
    """Carga config.json y system_prompt.md de un agente."""
    config_path = agent_dir / "config.json"
    prompt_path = agent_dir / "system_prompt.md"

    if not config_path.exists():
        raise FileNotFoundError(f"Falta config.json en {agent_dir}")
    if not prompt_path.exists():
        raise FileNotFoundError(f"Falta system_prompt.md en {agent_dir}")

    config = json.loads(config_path.read_text(encoding="utf-8"))
    system_prompt = prompt_path.read_text(encoding="utf-8")

    return {**config, "system_prompt": system_prompt}


def build_payload(agent: dict) -> dict:
    """Construye el payload para la API de OpenWebUI."""
    agent_id = agent.get("id") or _slug(agent["name"])
    return {
        "id": agent_id,
        "name": agent["name"],
        "base_model_id": agent["base_model"],
        "params": {
            **agent.get("params", {}),
            "system": agent["system_prompt"],
        },
        "meta": {
            "description": agent.get("description", ""),
            "tags": [{"name": t} for t in agent.get("tags", [])],
        },
    }


def import_agent(agent_dir: Path) -> None:
    """Importa o actualiza un agente en OpenWebUI."""
    agent = load_agent(agent_dir)
    payload = build_payload(agent)
    agent_id = payload["id"]

    # Check if exists
    check = _get(f"/api/v1/models/{agent_id}")
    if check.status_code == 200:
        # Update: delete and recreate (OpenWebUI doesn't have PATCH for custom models)
        _delete(f"/api/v1/models/{agent_id}")

    resp = _post("/api/v1/models/create", payload)
    if resp.status_code == 200:
        print(f"  ✅ {agent['name']} ({agent_id})")
    else:
        print(f"  ❌ {agent['name']}: {resp.status_code} — {resp.text[:200]}")


def import_all() -> None:
    """Importa todos los agentes del repo a OpenWebUI."""
    print(f"\n🚀 Importando agentes a {BASE_URL}\n")
    for agent_dir in sorted(AGENTS_DIR.iterdir()):
        if agent_dir.is_dir() and (agent_dir / "config.json").exists():
            print(f"  → {agent_dir.name}...")
            try:
                import_agent(agent_dir)
            except Exception as e:
                print(f"  ❌ Error en {agent_dir.name}: {e}")
    print("\n✅ Import completo.\n")


# ---------------------------------------------------------------------------
# Export: OpenWebUI → repo
# ---------------------------------------------------------------------------

def export_all() -> None:
    """Exporta los modelos custom de OpenWebUI al repo."""
    print(f"\n📦 Exportando agentes desde {BASE_URL}\n")

    resp = _get("/api/v1/models")
    if resp.status_code != 200:
        print(f"❌ No se pudo listar modelos: {resp.status_code} — {resp.text[:200]}")
        sys.exit(1)

    models = resp.json()
    # OpenWebUI devuelve una lista o un objeto con "data"
    if isinstance(models, dict):
        models = models.get("data", [])

    custom_models = [m for m in models if m.get("owned_by") == "openwebui"]

    if not custom_models:
        print("  No se encontraron modelos custom. Nada que exportar.")
        return

    for model in custom_models:
        agent_id = model["id"]
        name = model.get("name", agent_id)
        agent_dir = AGENTS_DIR / agent_id
        agent_dir.mkdir(parents=True, exist_ok=True)

        # Extraer system prompt
        system_prompt = (
            model.get("params", {}).get("system")
            or model.get("info", {}).get("params", {}).get("system", "")
        )

        # Reconstruir config.json
        config = {
            "id": agent_id,
            "name": name,
            "base_model": model.get("base_model_id", ""),
            "description": model.get("meta", {}).get("description", ""),
            "params": {
                k: v for k, v in model.get("params", {}).items() if k != "system"
            },
            "tags": [t["name"] for t in model.get("meta", {}).get("tags", [])],
        }

        (agent_dir / "config.json").write_text(
            json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        (agent_dir / "system_prompt.md").write_text(system_prompt, encoding="utf-8")
        print(f"  ✅ {name} → agents/{agent_id}/")

    print("\n✅ Export completo. Revisá con `git diff` antes de commitear.\n")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("import", "export"):
        print("Uso: python3 scripts/openwebui_api.py [import|export]")
        sys.exit(1)

    action = sys.argv[1]
    if action == "import":
        import_all()
    elif action == "export":
        export_all()
