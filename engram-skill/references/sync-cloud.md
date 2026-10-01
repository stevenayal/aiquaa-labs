# Sincronización — git y cloud

El SQLite local siempre es la fuente de verdad. Ambas formas de sync son **opt-in**: la skill
no las activa ni commitea `.engram/` sin que el usuario lo pida.

## Sync por git (chunks comprimidos)

Exporta las memorias nuevas como chunks JSONL gzip con un manifest — sin conflictos de merge
ni archivos gigantes.

```bash
engram sync                       # exporta memorias nuevas del proyecto a .engram/chunks/
engram sync --project mi-proyecto # solo ese proyecto
engram sync --all                 # todos los proyectos
git add .engram/ && git commit -m "sync engram memories"

# en otra máquina, después de git pull
engram sync --import              # importa chunks del manifest aún no importados
engram sync --status              # chunks locales vs remotos
```

```
.engram/
├── manifest.json
├── config.json        # opcional: { "project_name": "..." }
└── chunks/*.jsonl.gz
```

Antes de commitear `.engram/` en un repo compartido (p. ej. el repo de entregas del curso),
confirmar con el usuario: **todo** lo guardado en ese proyecto queda en el historial de git.
Por eso la regla de nunca guardar secretos en memoria.

## Cloud (replicación opcional)

Siempre por proyecto (`--project` obligatorio; `engram sync --cloud --all` está bloqueado a
propósito).

Prueba local con Docker:

```bash
docker compose -f docker-compose.cloud.yml up -d       # desde el repo de engram
engram cloud config --server http://127.0.0.1:18080
engram cloud enroll mi-proyecto
engram sync --cloud --project mi-proyecto
engram cloud status
```

- El token del cliente va por `ENGRAM_CLOUD_TOKEN` (variable de entorno, nunca en archivos
  versionados).
- Autosync: `ENGRAM_CLOUD_AUTOSYNC=1` + `ENGRAM_CLOUD_SERVER` + `ENGRAM_CLOUD_TOKEN`, con
  `engram serve` corriendo. `engram cloud status` → la línea `Local daemon:` dice si está vivo.
- Base existente → flujo guiado: `engram cloud upgrade doctor|repair --dry-run|bootstrap|status
  --project P`.
- Si el sync queda bloqueado: `engram doctor` / `engram cloud upgrade doctor` primero; engram
  nunca aplica reparaciones automáticamente desde el sync.

Detalle completo: `docs/engram-cloud/` y `DOCS.md#cloud-cli-opt-in` en el repo de engram.
