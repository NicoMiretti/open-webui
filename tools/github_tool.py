"""
Tool: github_tool
Interactuar con repositorios de GitHub via REST API.
Requiere variable de entorno: GITHUB_TOKEN
"""

import os
import json
import base64
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

GITHUB_API = "https://api.github.com"


class Tools:
    def __init__(self):
        self.token = os.environ.get("GITHUB_TOKEN", "")

    def _request(self, method: str, endpoint: str, body: dict = None) -> dict:
        url = f"{GITHUB_API}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        }
        data = json.dumps(body).encode() if body else None
        req = Request(url, data=data, headers=headers, method=method)
        try:
            with urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode())
        except HTTPError as e:
            return {"error": f"HTTP {e.code}: {e.reason}"}
        except URLError as e:
            return {"error": f"URL error: {e.reason}"}

    def get_pull_request(self, owner: str, repo: str, pr_number: int) -> str:
        """
        Obtiene los detalles de un Pull Request.
        :param owner: Dueño del repositorio.
        :param repo: Nombre del repositorio.
        :param pr_number: Número del PR.
        :return: Resumen del PR como string.
        """
        pr = self._request("GET", f"/repos/{owner}/{repo}/pulls/{pr_number}")
        if "error" in pr:
            return f"[ERROR] {pr['error']}"
        files = self._request("GET", f"/repos/{owner}/{repo}/pulls/{pr_number}/files")
        file_list = ""
        if isinstance(files, list):
            file_list = "\n".join(
                f"  - {f['filename']} (+{f['additions']}/-{f['deletions']})" for f in files[:20]
            )
        return (
            f"## PR #{pr_number}: {pr.get('title')}\n"
            f"**Estado:** {pr.get('state')} | **Draft:** {pr.get('draft')}\n"
            f"**Autor:** {pr.get('user', {}).get('login')}\n"
            f"**Branch:** `{pr.get('head', {}).get('ref')}` → `{pr.get('base', {}).get('ref')}`\n"
            f"**URL:** {pr.get('html_url')}\n\n"
            f"### Descripción\n{pr.get('body') or '_Sin descripción_'}\n\n"
            f"### Archivos modificados\n{file_list}"
        )

    def list_issues(self, owner: str, repo: str, state: str = "open", limit: int = 20) -> str:
        """
        Lista los issues de un repositorio.
        :param owner: Dueño del repositorio.
        :param repo: Nombre del repositorio.
        :param state: 'open', 'closed' o 'all'.
        :param limit: Cantidad máxima de issues a retornar.
        :return: Lista de issues como string.
        """
        issues = self._request("GET", f"/repos/{owner}/{repo}/issues?state={state}&per_page={limit}")
        if isinstance(issues, dict) and "error" in issues:
            return f"[ERROR] {issues['error']}"
        if not issues:
            return "No se encontraron issues."
        lines = [f"## Issues ({state}) — {owner}/{repo}\n"]
        for issue in issues:
            if "pull_request" in issue:
                continue
            labels = ", ".join(l["name"] for l in issue.get("labels", []))
            lines.append(
                f"- **#{issue['number']}** {issue['title']} "
                f"[{labels or 'sin etiquetas'}] — @{issue['user']['login']}"
            )
        return "\n".join(lines)

    def get_file_content(self, owner: str, repo: str, file_path: str, ref: str = "main") -> str:
        """
        Obtiene el contenido de un archivo en un repositorio de GitHub.
        :param owner: Dueño del repositorio.
        :param repo: Nombre del repositorio.
        :param file_path: Ruta al archivo en el repo.
        :param ref: Branch, tag o commit SHA.
        :return: Contenido del archivo como string.
        """
        data = self._request("GET", f"/repos/{owner}/{repo}/contents/{file_path}?ref={ref}")
        if "error" in data:
            return f"[ERROR] {data['error']}"
        if data.get("encoding") == "base64":
            content = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
            return f"# {file_path} @ {ref}\n\n{content}"
        return f"[ERROR] Encoding inesperado: {data.get('encoding')}"

    def create_issue_comment(self, owner: str, repo: str, issue_number: int, body: str) -> str:
        """
        Publica un comentario en un issue o PR.
        :param owner: Dueño del repositorio.
        :param repo: Nombre del repositorio.
        :param issue_number: Número de issue o PR.
        :param body: Cuerpo del comentario en markdown.
        :return: Mensaje de éxito o error.
        """
        result = self._request(
            "POST",
            f"/repos/{owner}/{repo}/issues/{issue_number}/comments",
            {"body": body}
        )
        if "error" in result:
            return f"[ERROR] {result['error']}"
        return f"✅ Comentario publicado: {result.get('html_url')}"
