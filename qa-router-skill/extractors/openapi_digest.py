#!/usr/bin/env python3
"""OpenAPI (JSON) → tabla de endpoints filtrable. Tier 0.

Uso: openapi_digest.py <openapi.json> [--tag <tag>] [--grep <substring>] [--schemas]
Pensado para no cargar el spec completo del sandbox (32 endpoints) por un grupo.
"""
import sys
import time

from _common import check_file, emit, fail, footer, load_json, now_iso, truncate

METHODS = ("get", "post", "put", "patch", "delete", "head", "options")


def main(argv):
    if len(argv) < 2:
        fail(__doc__, 2)
    path = argv[1]
    args = argv[2:]
    tag = grep = None
    for i, a in enumerate(args):
        if a == "--tag" and i + 1 < len(args):
            tag = args[i + 1].lower()
        if a == "--grep" and i + 1 < len(args):
            grep = args[i + 1].lower()
    show_schemas = "--schemas" in args

    started = time.time()
    raw = check_file(path)
    spec = load_json(path)
    paths = spec.get("paths")
    if not isinstance(paths, dict):
        fail(f"'{path}' no parece un spec OpenAPI (falta 'paths')")

    info = spec.get("info") or {}
    rows, total = [], 0
    for route, ops in sorted(paths.items()):
        if not isinstance(ops, dict):
            continue
        for method in METHODS:
            op = ops.get(method)
            if not isinstance(op, dict):
                continue
            total += 1
            tags = [str(t).lower() for t in op.get("tags") or []]
            if tag and tag not in tags:
                continue
            if grep and grep not in (route + " " + str(op.get("summary", ""))).lower():
                continue
            required = [p.get("name") for p in op.get("parameters") or []
                        if p.get("required")]
            body = "body" if op.get("requestBody") else ""
            codes = ",".join(sorted((op.get("responses") or {}).keys()))
            extra = " · ".join(x for x in (
                f"req: {','.join(str(r) for r in required)}" if required else "",
                body, f"→ {codes}" if codes else "") if x)
            rows.append(f"  {method.upper():6} {route} · "
                        f"{truncate(op.get('summary') or op.get('operationId') or '', 60)}"
                        + (f" · {extra}" if extra else ""))

    filt = f" (filtro: {tag or grep})" if (tag or grep) else ""
    lines = [
        f"OPENAPI · {info.get('title', '?')} v{info.get('version', '?')} · {now_iso()}",
        f"ENDPOINTS: {len(rows)} de {total}{filt}",
    ] + rows
    if not rows:
        lines.append("  (ningún endpoint coincide con el filtro)")
    if show_schemas:
        schemas = ((spec.get("components") or {}).get("schemas") or {})
        lines.append(f"SCHEMAS ({len(schemas)}):")
        for name, sch in sorted(schemas.items()):
            props = list((sch.get("properties") or {}).keys())
            lines.append(f"  {name}: {', '.join(props[:12])}"
                         + (" …" if len(props) > 12 else ""))
    lines.append(footer(path, raw))
    emit(lines, raw, "openapi", path, started)


if __name__ == "__main__":
    main(sys.argv)
