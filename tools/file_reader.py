"""
Tool: file_reader
Leer archivos y listar directorios del filesystem local.
"""

from pathlib import Path


class Tools:
    def __init__(self):
        pass

    def read_file(self, file_path: str, max_lines: int = 300) -> str:
        """
        Lee un archivo del filesystem y devuelve su contenido.
        :param file_path: Ruta absoluta o relativa al archivo.
        :param max_lines: Máximo de líneas a retornar (0 = sin límite).
        :return: Contenido del archivo como string.
        """
        try:
            path = Path(file_path).expanduser().resolve()
            if not path.exists():
                return f"[ERROR] Archivo no encontrado: {path}"
            if not path.is_file():
                return f"[ERROR] La ruta no es un archivo: {path}"
            blocked = [".env", "id_rsa", "id_ed25519", ".pem", ".key"]
            if any(path.name == b.lstrip(".") or path.name.endswith(b) for b in blocked):
                return f"[BLOQUEADO] Archivo sensible: {path.name}"
            size_kb = path.stat().st_size / 1024
            if size_kb > 512:
                return f"[ERROR] Archivo muy grande ({size_kb:.0f} KB). Máximo 512 KB."
            content = path.read_text(encoding="utf-8", errors="replace")
            lines = content.splitlines()
            if max_lines and len(lines) > max_lines:
                truncated = "\n".join(lines[:max_lines])
                return f"# {path}\n# [Truncado: {max_lines} de {len(lines)} líneas]\n\n{truncated}"
            return f"# {path}\n\n{content}"
        except PermissionError:
            return f"[ERROR] Permiso denegado: {file_path}"
        except Exception as e:
            return f"[ERROR] No se pudo leer el archivo: {e}"

    def list_directory(self, dir_path: str, depth: int = 2) -> str:
        """
        Lista el contenido de un directorio en forma de árbol.
        :param dir_path: Ruta al directorio.
        :param depth: Niveles de profundidad (default 2).
        :return: Árbol de directorios como string.
        """
        try:
            path = Path(dir_path).expanduser().resolve()
            if not path.exists():
                return f"[ERROR] Directorio no encontrado: {path}"
            if not path.is_dir():
                return f"[ERROR] No es un directorio: {path}"
            lines = [str(path)]
            def _walk(current: Path, current_depth: int, prefix: str):
                if current_depth > depth:
                    return
                try:
                    entries = sorted(current.iterdir(), key=lambda p: (p.is_file(), p.name))
                except PermissionError:
                    return
                for i, entry in enumerate(entries):
                    is_last = i == len(entries) - 1
                    connector = "└── " if is_last else "├── "
                    lines.append(f"{prefix}{connector}{entry.name}")
                    if entry.is_dir():
                        extension = "    " if is_last else "│   "
                        _walk(entry, current_depth + 1, prefix + extension)
            _walk(path, 1, "")
            return "\n".join(lines)
        except Exception as e:
            return f"[ERROR] No se pudo listar el directorio: {e}"
