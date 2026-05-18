"""
Tool: project_manager
Gestión del backlog y estado del proyecto en archivos markdown locales.
Permite al PM Agent leer y actualizar el backlog sin salir del chat.
"""

import json
import re
from datetime import datetime
from pathlib import Path

BACKLOG_FILE = "BACKLOG.md"
ADR_DIR = "docs/adr"


class Tools:
    def __init__(self):
        pass

    def read_backlog(self, project_path: str = ".") -> str:
        """
        Lee el backlog actual del proyecto.
        :param project_path: Ruta raíz del proyecto.
        :return: Contenido del backlog como string.
        """
        path = Path(project_path) / BACKLOG_FILE
        if not path.exists():
            return f"[INFO] No existe backlog en {path}. Podés crearlo con create_backlog()."
        return path.read_text(encoding="utf-8")

    def create_backlog(self, project_path: str, content: str) -> str:
        """
        Crea o sobreescribe el archivo BACKLOG.md con el contenido dado.
        :param project_path: Ruta raíz del proyecto.
        :param content: Contenido markdown del backlog.
        :return: Mensaje de confirmación.
        """
        path = Path(project_path) / BACKLOG_FILE
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"✅ Backlog guardado en {path}"

    def list_adrs(self, project_path: str = ".") -> str:
        """
        Lista todos los ADRs del proyecto.
        :param project_path: Ruta raíz del proyecto.
        :return: Lista de ADRs como string.
        """
        adr_path = Path(project_path) / ADR_DIR
        if not adr_path.exists():
            return f"[INFO] No existe directorio ADR en {adr_path}."
        adrs = sorted(adr_path.glob("*.md"))
        if not adrs:
            return "[INFO] No hay ADRs todavía."
        lines = [f"## ADRs en {adr_path}\n"]
        for adr in adrs:
            content = adr.read_text(encoding="utf-8", errors="replace")
            # Extraer título y estado
            title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
            status_match = re.search(r'\*\*Status[:\*]+\s*(.+)', content, re.IGNORECASE)
            title = title_match.group(1) if title_match else adr.stem
            status = status_match.group(1).strip() if status_match else "?"
            lines.append(f"- **{adr.name}** — {title} [{status}]")
        return "\n".join(lines)

    def create_adr(self, project_path: str, adr_number: str, title: str, content: str) -> str:
        """
        Crea un nuevo ADR en el directorio docs/adr/.
        :param project_path: Ruta raíz del proyecto.
        :param adr_number: Número del ADR (ej: '001').
        :param title: Título corto del ADR.
        :param content: Contenido completo en markdown.
        :return: Mensaje de confirmación.
        """
        adr_path = Path(project_path) / ADR_DIR
        adr_path.mkdir(parents=True, exist_ok=True)
        slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
        filename = f"ADR-{adr_number}-{slug}.md"
        file_path = adr_path / filename
        file_path.write_text(content, encoding="utf-8")
        return f"✅ ADR creado: {file_path}"

    def get_project_status(self, project_path: str = ".") -> str:
        """
        Devuelve un resumen rápido del estado del proyecto.
        :param project_path: Ruta raíz del proyecto.
        :return: Resumen como string.
        """
        root = Path(project_path)
        lines = [f"## Estado del proyecto: {root.resolve()}\n"]

        # Backlog
        backlog = root / BACKLOG_FILE
        lines.append(f"- Backlog: {'✅ existe' if backlog.exists() else '❌ no existe'}")

        # ADRs
        adr_path = root / ADR_DIR
        adr_count = len(list(adr_path.glob("*.md"))) if adr_path.exists() else 0
        lines.append(f"- ADRs: {adr_count}")

        # Tests
        test_dirs = list(root.glob("tests/")) + list(root.glob("test/"))
        lines.append(f"- Directorio de tests: {'✅' if test_dirs else '❌ no encontrado'}")

        # Archivos clave
        for fname in ["README.md", "pyproject.toml", "requirements.txt", "docker-compose.yml", ".env.example"]:
            exists = (root / fname).exists()
            lines.append(f"- {fname}: {'✅' if exists else '—'}")

        return "\n".join(lines)
