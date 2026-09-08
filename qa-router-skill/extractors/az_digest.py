#!/usr/bin/env python3
"""Payload JSON de Azure DevOps → solo los campos que pide metrics-spec. Tier 0.

Uso: az_digest.py <payload.json> [--fields a,b,c]
Reconoce las formas que consume qa-productivity-skill (pullRequests, resultsByTest,
runs/value genéricos) y proyecta campos; con --fields fuerza la proyección.
"""
import sys
import time

from _common import (MAX_ROWS, check_file, emit, fail, footer, load_json,
                     now_iso, truncate)

DEFAULT_FIELDS = ("id", "name", "title", "state", "status", "result", "outcome",
                  "createdDate", "creationDate", "finishTime", "pullRequestId")


def dig(obj, dotted):
    cur = obj
    for part in dotted.split("."):
        if isinstance(cur, dict):
            cur = cur.get(part)
        else:
            return None
    return cur


def project(row, fields):
    out = []
    for f in fields:
        val = dig(row, f)
        if val not in (None, "", [], {}):
            out.append(f"{f.split('.')[-1]}={truncate(val, 60)}")
    return " · ".join(out)


def main(argv):
    if len(argv) < 2:
        fail(__doc__, 2)
    path = argv[1]
    fields = None
    args = argv[2:]
    for i, a in enumerate(args):
        if a == "--fields" and i + 1 < len(args):
            fields = [f.strip() for f in args[i + 1].split(",") if f.strip()]

    started = time.time()
    raw = check_file(path)
    data = load_json(path)
    if not isinstance(data, dict):
        fail(f"'{path}' no es un objeto JSON de Azure DevOps")

    lines = [f"AZURE DEVOPS · {path.split('/')[-1]} · {now_iso()}"]
    handled = False

    if isinstance(data.get("resultsByTest"), dict):
        handled = True
        results = data["resultsByTest"]
        lines.append(f"RESULTADOS POR TEST ({len(results)}):")
        for test, runs in results.items():
            outcomes = [r.get("outcome") for r in runs]
            failed = sum(1 for o in outcomes if o == "Failed")
            flag = "  ⚠ inestable" if failed and failed < len(outcomes) else ""
            lines.append(f"  {test} · {len(runs)} corridas · "
                         f"{len(outcomes) - failed} ok / {failed} fallo(s){flag}")

    for key in ("pullRequests", "value", "runs", "workItems"):
        rows = data.get(key)
        if not isinstance(rows, list) or not rows:
            continue
        handled = True
        use = fields or [f for f in DEFAULT_FIELDS
                         if any(dig(r, f) is not None for r in rows[:20])]
        use += [f for f in ("createdBy.uniqueName", "repository.name") if not fields]
        lines.append(f"{key.upper()} ({len(rows)}):")
        for row in rows[:MAX_ROWS]:
            body = project(row, use)
            extra = row.get("relatedTestCaseIds")
            lines.append(f"  {body}" + (f" · testCases={extra}" if extra else ""))
        if len(rows) > MAX_ROWS:
            lines.append(f"  … {len(rows) - MAX_ROWS} más (usá --fields para acotar)")

    if not handled:
        fail(f"'{path}' no tiene ninguna forma conocida de Azure DevOps "
             f"(pullRequests/value/runs/workItems/resultsByTest). Claves: "
             f"{sorted(data.keys())[:10]}")

    lines.append(footer(path, raw))
    emit(lines, raw, "azure-devops", path, started)


if __name__ == "__main__":
    main(sys.argv)
