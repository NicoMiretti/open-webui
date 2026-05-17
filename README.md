# OpenWebUI Config — GitOps

Repositorio de configuración para entorno de desarrollo asistido por IA en OpenWebUI.  
Permite versionar, reproducir y actualizar agentes, tools y knowledge bases en cualquier instancia.

## Estructura

```
openwebui-config/
├── agents/              # Un agente por carpeta: config.json + system_prompt.md
│   ├── architect/       # Diseño, ADRs, decisiones técnicas
│   ├── dev/             # Generación, revisión y refactor de código
│   ├── qa/              # Testing, estrategia de pruebas, edge cases
│   └── pm/              # Planning, stories, backlog, estimaciones
├── tools/               # Tools Python disponibles para los agentes
├── knowledge/           # Instrucciones para las Knowledge Bases (RAG)
├── scripts/             # Import/export y CLI para interactuar con OpenWebUI API
└── .github/workflows/   # CI: validación de configs y prompts
```

## Quickstart

### 1. Configurar variables de entorno

```bash
cp .env.example .env
# Editá .env con tu URL e API token de OpenWebUI
```

### 2. Importar toda la configuración a OpenWebUI

```bash
pip install requests python-dotenv
bash scripts/import.sh
```

### 3. Exportar cambios hechos desde la UI al repo

```bash
bash scripts/export.sh
git diff
git add -A && git commit -m "chore: sync agents from UI"
```

## Flujo GitOps

```
Editar system_prompt.md o config.json en Git
        ↓
git commit + push
        ↓
GitHub Actions valida JSONs y prompts
        ↓
bash scripts/import.sh   (manual o vía CD)
        ↓
OpenWebUI actualizado
```

## Flujo de desarrollo con los agentes

Para cualquier nueva feature, el flujo recomendado es:

```
1. PM Agent      → Descomposición en stories + criterios de aceptación
2. Architect Agent → Diseño técnico + ADR si aplica
3. Dev Agent     → Implementación + esqueleto de tests
4. QA Agent      → Tests completos + revisión de cobertura
5. Dev Agent     → Fixes y ajustes finales
6. Architect Agent → Sign-off y documentación de decisiones
```

## Agentes

| Agente | Temperatura | Especialidad |
|--------|-------------|--------------|
| 🏗️ Architect Agent | 0.2 | Diseño, C4, ADRs, revisión de arquitectura |
| 💻 Dev Agent | 0.2 | FastAPI/Python, generación y revisión de código |
| 🧪 QA Agent | 0.2 | pytest, estrategia de tests, edge cases |
| 📋 PM Agent | 0.5 | Stories, backlog, estimaciones, planning |

## Requisitos

- OpenWebUI >= 0.4.x
- Python >= 3.10
- Modelo base configurado (ej: Gemini 2.0 Flash Lite vía API)
