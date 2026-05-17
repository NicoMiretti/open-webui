# Architecture — [Nombre del Proyecto]

> Documento vivo. Actualizar al cerrar cada sprint o cuando cambie la arquitectura.  
> Última actualización: YYYY-MM-DD

---

## 1. Visión general

[2-3 párrafos describiendo qué hace el sistema, para quién, y cuál es su propósito de negocio.]

---

## 2. Stack tecnológico

| Capa | Tecnología | Versión | Notas |
|------|-----------|---------|-------|
| Backend | FastAPI | x.x | ... |
| ORM | SQLAlchemy | 2.x | Async |
| Base de datos | PostgreSQL | 15 | ... |
| Frontend | React / HTMX | ... | ... |
| Auth | JWT / OAuth2 | — | ... |
| Queue | Celery + Redis | — | Opcional |
| CI/CD | GitHub Actions | — | ... |
| Deploy | Docker / Railway / ... | — | ... |

---

## 3. Diagrama de contexto (C4 — Level 1)

```mermaid
C4Context
    title Context Diagram — [Proyecto]

    Person(user, "Usuario", "Descripción del usuario principal")
    System(system, "[Nombre del sistema]", "Descripción breve")
    System_Ext(ext1, "Sistema externo", "Descripción")

    Rel(user, system, "Usa")
    Rel(system, ext1, "Llama a", "HTTPS/REST")
```

---

## 4. Diagrama de contenedores (C4 — Level 2)

```mermaid
C4Container
    title Container Diagram — [Proyecto]

    Person(user, "Usuario")

    Container(frontend, "Frontend", "React / HTMX", "Interfaz de usuario")
    Container(api, "API", "FastAPI", "Lógica de negocio y endpoints REST")
    Container(db, "Database", "PostgreSQL", "Almacenamiento principal")
    Container(queue, "Queue", "Redis + Celery", "Tareas asíncronas")

    Rel(user, frontend, "Usa", "HTTPS")
    Rel(frontend, api, "Llama", "HTTPS/REST")
    Rel(api, db, "Lee/Escribe", "SQL")
    Rel(api, queue, "Encola tareas", "Redis protocol")
```

---

## 5. Estructura del proyecto

```
project/
├── app/
│   ├── core/            # Config, DB, middleware, logging
│   ├── features/        # Un módulo por feature (router, service, repo, schemas)
│   │   └── users/
│   │       ├── router.py
│   │       ├── service.py
│   │       ├── repository.py
│   │       ├── schemas.py
│   │       ├── models.py
│   │       └── exceptions.py
│   └── main.py
├── tests/
│   ├── conftest.py
│   └── features/
│       └── users/
├── alembic/             # Migraciones de DB
├── docker/
├── .github/workflows/
└── pyproject.toml
```

---

## 6. Decisiones de arquitectura (ADRs)

| ADR | Título | Estado |
|-----|--------|--------|
| ADR-001 | [Título] | Accepted |

---

## 7. Consideraciones de seguridad

- Autenticación: [método]
- Autorización: [modelo de permisos]
- Datos sensibles: [cómo se manejan]
- Secretos: [dónde viven, cómo se inyectan]

---

## 8. Consideraciones de despliegue

[Cómo se despliega, variables de entorno requeridas, dependencias externas.]
