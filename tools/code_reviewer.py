"""
Tool: code_reviewer
Analiza código Python: complejidad, code smells, métricas básicas.
No requiere dependencias externas.
"""

import ast
import re
from pathlib import Path


class Tools:
    def __init__(self):
        pass

    def analyze_python_file(self, file_path: str) -> str:
        """
        Analiza un archivo Python y devuelve métricas y code smells.
        :param file_path: Ruta al archivo .py a analizar.
        :return: Reporte de análisis como string.
        """
        try:
            path = Path(file_path).expanduser().resolve()
            if not path.exists():
                return f"[ERROR] Archivo no encontrado: {path}"
            source = path.read_text(encoding="utf-8", errors="replace")
            return self.analyze_python_code(source, str(path))
        except Exception as e:
            return f"[ERROR] {e}"

    def analyze_python_code(self, source_code: str, filename: str = "<string>") -> str:
        """
        Analiza código Python en string y devuelve métricas y code smells.
        :param source_code: Código Python como string.
        :param filename: Nombre del archivo (para el reporte).
        :return: Reporte de análisis como string.
        """
        issues = []
        metrics = {}

        lines = source_code.splitlines()
        metrics["total_lines"] = len(lines)
        metrics["blank_lines"] = sum(1 for l in lines if not l.strip())
        metrics["comment_lines"] = sum(1 for l in lines if l.strip().startswith("#"))

        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            return f"[ERROR SINTAXIS] {e}"

        functions = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        metrics["functions"] = len(functions)
        metrics["classes"] = len(classes)

        # Funciones largas
        for func in functions:
            func_lines = func.end_lineno - func.lineno + 1
            if func_lines > 50:
                issues.append(f"[COMPLEJIDAD] `{func.name}` tiene {func_lines} líneas (máx recomendado: 50)")

        # Funciones sin type hints
        for func in functions:
            missing_hints = []
            for arg in func.args.args:
                if arg.annotation is None and arg.arg not in ("self", "cls"):
                    missing_hints.append(arg.arg)
            if missing_hints:
                issues.append(f"[TYPE HINTS] `{func.name}` — args sin type hint: {', '.join(missing_hints)}")
            if func.returns is None and func.name != "__init__":
                issues.append(f"[TYPE HINTS] `{func.name}` — falta tipo de retorno")

        # Funciones sin docstring
        for func in functions:
            if not (func.body and isinstance(func.body[0], ast.Expr) and isinstance(func.body[0].value, ast.Constant)):
                issues.append(f"[DOCSTRING] `{func.name}` no tiene docstring")

        # Bare except
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                issues.append(f"[SEGURIDAD] `except` sin tipo en línea {node.lineno} — captura demasiado")

        # Magic numbers
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                if node.value not in (0, 1, -1, True, False) and not isinstance(node.value, bool):
                    issues.append(f"[MAGIC NUMBER] Valor literal `{node.value}` en línea {node.lineno}")

        # Imports con *
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name == "*":
                        issues.append(f"[IMPORT] `from {node.module} import *` — evitar imports con wildcard")

        # Líneas muy largas
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                issues.append(f"[ESTILO] Línea {i} tiene {len(line)} caracteres (máx: 120)")

        # Construir reporte
        report = [f"## Análisis: {filename}\n"]
        report.append("### Métricas")
        report.append(f"- Líneas totales: {metrics['total_lines']}")
        report.append(f"- Funciones: {metrics['functions']}")
        report.append(f"- Clases: {metrics['classes']}")
        report.append(f"- Líneas en blanco: {metrics['blank_lines']}")
        report.append(f"- Comentarios: {metrics['comment_lines']}")

        if issues:
            report.append(f"\n### Issues encontrados ({len(issues)})")
            for issue in issues:
                report.append(f"- {issue}")
        else:
            report.append("\n### ✅ Sin issues detectados")

        return "\n".join(report)
