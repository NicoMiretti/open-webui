"""
Tool: web_search
Búsqueda web via DuckDuckGo (sin API key requerida).
Útil para buscar documentación, CVEs, ejemplos de código, librerías.
"""

import json
from urllib.request import urlopen, Request
from urllib.parse import urlencode
from urllib.error import URLError


class Tools:
    def __init__(self):
        pass

    def search(self, query: str, max_results: int = 5) -> str:
        """
        Realiza una búsqueda web y devuelve los resultados más relevantes.
        :param query: Término de búsqueda.
        :param max_results: Cantidad máxima de resultados (default 5).
        :return: Resultados como string con título, URL y descripción.
        """
        try:
            params = urlencode({
                "q": query,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1,
            })
            url = f"https://api.duckduckgo.com/?{params}"
            req = Request(url, headers={"User-Agent": "openwebui-agent/1.0"})
            with urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode())

            results = []

            # Abstract (respuesta directa de DuckDuckGo)
            if data.get("AbstractText"):
                results.append(
                    f"**Respuesta directa:**\n{data['AbstractText']}\n"
                    f"Fuente: {data.get('AbstractURL', '')}"
                )

            # Related topics
            for topic in data.get("RelatedTopics", [])[:max_results]:
                if isinstance(topic, dict) and topic.get("Text"):
                    results.append(
                        f"- {topic['Text']}\n  {topic.get('FirstURL', '')}"
                    )

            if not results:
                return (
                    f"No se encontraron resultados directos para: '{query}'.\n"
                    f"Sugerencia: intentá con términos más específicos o en inglés."
                )

            header = f"## Resultados para: '{query}'\n\n"
            return header + "\n\n".join(results[:max_results])

        except URLError as e:
            return f"[ERROR] No se pudo conectar a DuckDuckGo: {e.reason}"
        except Exception as e:
            return f"[ERROR] Búsqueda fallida: {e}"

    def search_docs(self, library: str, topic: str) -> str:
        """
        Busca en la documentación de una librería específica.
        :param library: Nombre de la librería (ej: 'fastapi', 'sqlalchemy', 'pytest').
        :param topic: Tema a buscar dentro de la librería.
        :return: Resultados de búsqueda enfocados en documentación.
        """
        query = f"{library} {topic} documentation site:docs.{library}.com OR site:fastapi.tiangolo.com OR site:docs.sqlalchemy.org"
        return self.search(query)
