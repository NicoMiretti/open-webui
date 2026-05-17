# Convenciones de Código — [Nombre del Proyecto]

> Todo el código generado por agentes o escrito manualmente debe seguir estas convenciones.

---

## Python / FastAPI

### Estilo general
- **PEP8** estricto. Linter: `ruff`.
- Type hints en **todas** las funciones y variables de módulo.
- Docstrings en **todas** las funciones y clases públicas. Formato: Google style.
- `__all__` en todos los módulos.

### Nombres
- Módulos y paquetes: `snake_case`
- Clases: `PascalCase`
- Funciones y variables: `snake_case`
- Constantes: `UPPER_SNAKE_CASE`
- Schemas Pydantic: `PascalCase` con sufijo según tipo:
  - `UserCreateRequest`, `UserResponse`, `UserUpdateRequest`

### Estructura de una feature
```
app/features/<feature_name>/
├── router.py       # Solo HTTP: path, método, request/response, llama al service
├── service.py      # Lógica de negocio. Sin acceso directo a DB.
├── repository.py   # Solo acceso a DB. Sin lógica de negocio.
├── schemas.py      # Pydantic: Request, Response, internal DTOs
├── models.py       # SQLAlchemy ORM models
└── exceptions.py   # Excepciones del dominio (heredan de base exception)
```

### Manejo de errores
- Nunca `except Exception` a secas. Siempre capturar excepciones específicas.
- Loguear con `logger.exception(...)` antes de re-lanzar o transformar.
- Las excepciones de dominio van en `exceptions.py` y se transforman en HTTP errors en el router.

### Logging
```python
import logging
logger = logging.getLogger(__name__)
# Usar: logger.info / logger.warning / logger.error / logger.exception
# No usar: print()
```

### Configuración
- Todo via `pydantic-settings`. Nunca hardcoded.
- Un único `Settings` en `app/core/config.py`.

### Tests
- Naming: `test_<what>_when_<condition>_should_<expected>`
- Patrón: AAA (Arrange / Act / Assert) con comentarios de sección.
- Fixtures compartidas en `conftest.py`.
- Mocks: `pytest-mock` / `unittest.mock`. Nunca hits reales a DB o APIs externas en unit tests.

---

## Git

### Commits (Conventional Commits)
```
feat(scope): descripción corta en imperativo
fix(scope): descripción corta
refactor(scope): descripción corta
test(scope): descripción corta
docs(scope): descripción corta
chore(scope): descripción corta
```

### Branches
- `main` — producción, protegida
- `feat/<descripcion-corta>` — nuevas features
- `fix/<descripcion-corta>` — bug fixes
- `chore/<descripcion-corta>` — mantenimiento

### PRs
- Título: mismo formato que commit message.
- Descripción: qué cambió, por qué, cómo probarlo, checklist.
- Requiere: CI verde + al menos 1 review (si hay equipo).

---

## Frontend (si aplica)

- TypeScript estricto (`strict: true` en tsconfig).
- Componentes: functional, hooks.
- Naming de componentes: `PascalCase`.
- Naming de archivos de componentes: `PascalCase.tsx`.
- CSS: Tailwind utility classes. Sin CSS custom salvo variables globales.
