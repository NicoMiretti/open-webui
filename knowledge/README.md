# Knowledge Base — Instrucciones

Esta carpeta documenta **qué subir** a cada colección de la Knowledge Base en OpenWebUI.  
Los archivos en sí **no se versionar acá** (pueden ser grandes o propietarios).  
En su lugar, se documenta el inventario esperado y el propósito de cada documento.

---

## Cómo crear una colección en OpenWebUI

```
Workspace → Knowledge → "+ New Collection"
→ Nombre: project-core
→ Descripción: Documentación base del proyecto
→ Subir archivos (ver inventario abajo)
```

Cada agente que uses debe tener esta colección asociada:
```
Workspace → Models → [Agente] → Edit → Knowledge → seleccionar "project-core"
```

---

## Colección: `project-core`

Documentos que deben estar presentes **antes de empezar a trabajar** con los agentes.  
Esta colección es compartida por todos los agentes.

| Documento | Descripción | Formato | Prioridad |
|-----------|-------------|---------|-----------|
| `README.md` | Visión general del proyecto, objetivo, contexto de negocio | Markdown | 🔴 Alta |
| `ARCHITECTURE.md` | Descripción de la arquitectura actual, stack, decisiones principales | Markdown | 🔴 Alta |
| `ADR/` | Carpeta con todos los Architecture Decision Records | Markdown | 🔴 Alta |
| `openapi.yaml` / `openapi.json` | Contrato de la API (generado con FastAPI o escrito a mano) | YAML/JSON | 🟡 Media |
| `CONVENTIONS.md` | Guía de estilo, convenciones de código, naming, estructura de carpetas | Markdown | 🟡 Media |
| `DOMAIN_GLOSSARY.md` | Glosario de términos del dominio de negocio | Markdown | 🟡 Media |
| `ERD.md` / `schema.sql` | Modelo de datos, entidad-relación | Markdown/SQL | 🟡 Media |
| `BACKLOG.md` | Backlog actual con epics y stories | Markdown | 🟢 Baja |

---

## Templates incluidos

Para arrancar rápido, usá los templates en `knowledge/templates/`:

- `ARCHITECTURE.md` — Template de documento de arquitectura.
- `CONVENTIONS.md` — Template de convenciones de código para FastAPI/Python.
- `DOMAIN_GLOSSARY.md` — Template de glosario.
- `ADR-000-template.md` — Template de ADR.

---

## Mantenimiento

- **Al iniciar el proyecto:** subir todos los documentos de prioridad Alta.
- **Al cerrar cada sprint:** actualizar `BACKLOG.md` y cualquier ADR nuevo.
- **Al cambiar la arquitectura:** actualizar `ARCHITECTURE.md` y agregar el ADR correspondiente.
- **Al agregar endpoints:** actualizar `openapi.yaml`.

La Knowledge Base es la "memoria larga" del proyecto. Si un agente da respuestas inconsistentes con el proyecto real, probablemente falta un documento acá.
