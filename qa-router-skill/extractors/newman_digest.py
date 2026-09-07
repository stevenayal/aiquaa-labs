#!/usr/bin/env python3
"""newman JSON (--reporters json) → digest de fallos. Tier 0, 0 tokens LLM.

Uso: newman_digest.py <archivo.json> [--all]
     --all  incluye también los requests que pasaron (por defecto solo fallos)
"""
import sys
import time

from _common import (MAX_CLUSTERS, MAX_ROWS, check_file, cluster, emit, fail,
                     footer, load_json, now_iso, truncate)


def collect_failures(run):
    """Devuelve [(item, metodo, url, assert, motivo)] cubriendo el 100% de fallos.

    Prefiere run.failures (lo que newman emite de verdad); cae a escanear
    executions[].assertions[].error si el reporte no lo trae.
    """
    out = []
    for f in run.get("failures") or []:
        err = f.get("error") or {}
        src = f.get("source") or {}
        req = (f.get("at") or "")
        out.append((
            src.get("name") or f.get("parent", {}).get("name") or "?",
            (src.get("request") or {}).get("method") or "",
            _url(src.get("request") or {}),
            err.get("test") or err.get("name") or "?",
            truncate(err.get("message") or req or "?"),
        ))
    if out:
        return out
    for ex in run.get("executions") or []:
        for a in ex.get("assertions") or []:
            if not a.get("error"):
                continue
            err = a["error"]
            out.append((
                (ex.get("item") or {}).get("name", "?"),
                (ex.get("request") or {}).get("method", ""),
                _url(ex.get("request") or {}),
                a.get("assertion", "?"),
                truncate(err.get("message") or err.get("name") or "?"),
            ))
    return out


def _url(request):
    url = request.get("url")
    if isinstance(url, str):
        return url
    if isinstance(url, dict):
        raw = url.get("raw")
        if raw:
            return raw
        path = "/".join(str(p) for p in url.get("path") or [])
        return "/" + path
    return ""


def main(argv):
    if len(argv) < 2:
        fail(__doc__, 2)
    path = argv[1]
    show_all = "--all" in argv[2:]
    started = time.time()
    raw = check_file(path)
    data = load_json(path)

    run = data.get("run")
    if not isinstance(run, dict):
        fail(f"'{path}' no parece un reporte JSON de newman (falta 'run')")

    stats = run.get("stats") or {}
    reqs = stats.get("requests") or {}
    asserts = stats.get("assertions") or {}
    timings = run.get("timings") or {}
    dur = timings.get("completed", 0) - timings.get("started", 0)
    name = ((data.get("collection") or {}).get("info") or {}).get("name", "?")

    failures = collect_failures(run)
    lines = [
        f"NEWMAN · {name} · {now_iso()}",
        f"TOTALES: {reqs.get('total', '?')} requests · "
        f"{asserts.get('total', '?')} asserts · "
        f"{asserts.get('failed', len(failures))} fallos · {dur/1000:.1f}s",
    ]

    if failures:
        lines.append(f"FALLOS ({len(failures)}):")
        groups = cluster(failures, key_fn=lambda f: (f[0], f[3], f[4][:60]))
        for _, count, ex in groups[:MAX_CLUSTERS]:
            item, method, url, assertion, msg = ex
            suffix = f" ×{count}" if count > 1 else ""
            lines.append(f"  {method} {url} · \"{assertion}\" · {msg}{suffix}".rstrip())
        if len(groups) > MAX_CLUSTERS:
            rest = sum(c for _, c, _ in groups[MAX_CLUSTERS:])
            lines.append(f"  … {len(groups) - MAX_CLUSTERS} clusters más ({rest} fallos)")
        top = groups[0]
        if top[1] > 1:
            pct = 100 * top[1] / len(failures)
            lines.append(f"CLUSTERS: {top[1]}/{len(failures)} fallos ({pct:.0f}%) "
                         f"son \"{top[2][3]}\" en {top[2][0]}")
    else:
        lines.append("FALLOS: ninguno")

    if show_all:
        lines.append("REQUESTS:")
        for ex in (run.get("executions") or [])[:MAX_ROWS]:
            resp = ex.get("response") or {}
            lines.append(f"  {(ex.get('request') or {}).get('method', '')} "
                         f"{_url(ex.get('request') or {})} · "
                         f"{resp.get('code', '?')} · {resp.get('responseTime', '?')}ms")

    lines.append(footer(path, raw))
    emit(lines, raw, "newman", path, started)


if __name__ == "__main__":
    main(sys.argv)
