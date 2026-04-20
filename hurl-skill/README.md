# hurl-skill

> Automatización de pruebas de API con Hurl — formato declarativo, diff-friendly, CI-native — powered by [aiquaa](https://aiquaa.com/)

Skill para Claude Code, Cursor, Windsurf y 40+ agentes de IA. Genera archivos `.hurl`, variables de entorno, pipelines Azure Pipelines y reportes de resultados — todo con salidas ultra-compactas estilo caveman.

---

## ¿Por qué Hurl?

| Aspecto | Postman / Newman | Hurl |
|---------|-----------------|------|
| Formato | JSON propietario | Texto plano `.hurl` |
| Diff en git | Difícil | Trivial |
| Instalación en CI | `npm install -g newman` | Binario estático — sin runtime |
| Reporte Azure | Plugin externo (junit) | `--report-junit` nativo |
| Legibilidad LLMs | Baja | Alta |

Hurl complementa a Postman/Newman — no lo reemplaza. Postman para exploración, Hurl para CI declarativo y code review.

---

## ¿Qué incluye?

| Componente | Qué hace |
|------------|----------|
| `skills/hurl/SKILL.md` | Skill principal — genera `.hurl`, env vars, CI pipelines |
| `examples/H_EXAMPLE_API.hurl` | Colección de ejemplo lista para usar |
| `examples/V_EXAMPLE_API.env` | Variables de entorno de ejemplo |
| `examples/Y_EXAMPLE_API_hurl.yml` | Pipeline Azure Pipelines de ejemplo |

---

## Instalación

```bash
# Claude Code
npx skills add aiquaa-labs/hurl-skill

# Cursor
npx skills add aiquaa-labs/hurl-skill -a cursor

# Windsurf
npx skills add aiquaa-labs/hurl-skill -a windsurf

# Cualquier otro agente
npx skills add aiquaa-labs/hurl-skill
```

---

## Uso rápido

Activá la skill con cualquiera de estos triggers:

```
/hurl:generate   → generar .hurl desde spec / curl / código fuente
/hurl:add-test   → agregar assertions a un entry existente
/hurl:fix        → analizar y reparar un entry fallido
/hurl:ci         → generar pipeline Azure Pipelines
/hurl:env        → crear o actualizar archivo de variables .env
/hurl:run        → mostrar comando hurl y reportar resultados
```

La skill siempre recolecta contexto antes de generar — URL, endpoints, body, auth, validadores.

---

## Convención de nombres de archivos

| Tipo | Patrón | Ejemplo |
|------|--------|---------|
| Test file | `H_NOMBRE_DE_API.hurl` | `H_MYTHS_API.hurl` |
| Variables local | `V_NOMBRE_DE_API.env` | `V_MYTHS_API.env` |
| Variables staging | `V_NOMBRE_DE_API_STAGING.env` | `V_MYTHS_API_STAGING.env` |
| Pipeline Azure | `Y_NOMBRE_DE_API_hurl.yml` | `Y_MYTHS_API_hurl.yml` |

---

## Instalar Hurl localmente

```bash
# Windows (winget)
winget install Hurl.Hurl

# macOS (brew)
brew install hurl

# Ubuntu/Debian
apt-get install -y hurl

# Binario estático (cualquier plataforma)
curl -LO https://github.com/Orange-OpenSource/hurl/releases/latest/download/hurl-x86_64-unknown-linux-gnu.tar.gz
tar xzf hurl-*.tar.gz && mv hurl /usr/local/bin/
```

---

## Estructura del repositorio

```
hurl-skill/
├── skills/
│   └── hurl/
│       └── SKILL.md          → skill principal
├── examples/
│   ├── H_EXAMPLE_API.hurl    → tests de ejemplo
│   ├── V_EXAMPLE_API.env     → variables de ejemplo
│   └── Y_EXAMPLE_API_hurl.yml → pipeline Azure de ejemplo
├── docs/
│   └── uso.md                → guía de uso en español
└── .github/
    └── workflows/
        └── Y_HURL_SKILL_CI.yml → CI del propio skill
```

---

## Créditos

Creado por [aiquaa](https://aiquaa.com/) — *Saber es calidad*

Compatible con el stack [postman-newman-skill](https://github.com/aiquaa-labs/postman-newman-skill).

## Licencia

MIT
