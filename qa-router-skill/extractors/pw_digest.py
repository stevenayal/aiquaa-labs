#!/usr/bin/env python3
"""Reporte JSON de Playwright → digest de specs fallidos y flaky. Tier 0.

Uso: pw_digest.py <playwright-report.json>
Generalo con: npx playwright test --reporter=json > report.json
"""
import sys
import time

from _common import (MAX_CLUSTERS, check_file, cluster, emit, fail, footer,
                     load_json, now_iso, truncate)


def walk(suite, trail=()):
    """Aplana el árbol de suites de Playwright en (titulo, spec, test)."""
    title = suite.get("title", "")
    path = trail + ((title,) if title else ())
    for spec in suite.get("specs") or []:
        for test in spec.get("tests") or []:
            yield path, spec, test
    for child in suite.get("suites") or []:
        yield from walk(child, path)


def main(argv):
    if len(argv) < 2:
        fail(__doc__, 2)
    path = argv[1]
    started = time.time()
    raw = check_file(path)
    data = load_json(path)
    if "suites" not in data:
        fail(f"'{path}' no parece un reporte JSON de Playwright (falta 'suites')")

    total = passed = flaky = 0
    fails = []
    for trail, spec, test in walk({"suites": data.get("suites") or []}):
        total += 1
        status = test.get("status") or "unknown"
        results = test.get("results") or []
        retries = max(0, len(results) - 1)
        if status == "expected":
            passed += 1
            if retries:
                flaky += 1
            continue
        if status == "flaky":
            passed += 1
            flaky += 1
            continue
        if status == "skipped":
            continue
        err = ""
        where = ""
        for res in results:
            e = res.get("error") or {}
            if e:
                err = truncate(e.get("message") or "", 140)
                loc = e.get("location") or {}
                if loc:
                    where = f"{loc.get('file', '')}:{loc.get('line', '')}"
                break
        fails.append((" › ".join(t for t in trail if t) or spec.get("title", "?"),
                      spec.get("title", "?"),
                      f"{spec.get('file', '')}:{spec.get('line', '')}" or where,
                      err, retries))

    stats = data.get("stats") or {}
    dur = stats.get("duration")
    lines = [
        f"PLAYWRIGHT · {path.split('/')[-1]} · {now_iso()}",
        f"TOTALES: {total} tests · {passed} ok · {len(fails)} fallos · "
        f"{flaky} flaky" + (f" · {dur/1000:.1f}s" if isinstance(dur, (int, float)) else ""),
    ]
    if fails:
        lines.append(f"FALLOS ({len(fails)}):")
        groups = cluster(fails, key_fn=lambda f: f[3][:70])
        for _, count, ex in groups[:MAX_CLUSTERS]:
            suite, title, loc, err, retries = ex
            extra = f" · {retries} retries" if retries else ""
            suffix = f" ×{count}" if count > 1 else ""
            lines.append(f"  {suite} › {title} · {loc}{extra}{suffix}")
            lines.append(f"      ↳ {err}" if err else "      ↳ (sin mensaje de error)")
        if len(groups) > MAX_CLUSTERS:
            rest = sum(c for _, c, _ in groups[MAX_CLUSTERS:])
            lines.append(f"  … {len(groups) - MAX_CLUSTERS} clusters más ({rest} fallos)")
    else:
        lines.append("FALLOS: ninguno")
    if flaky:
        lines.append(f"FLAKY: {flaky} test(s) pasaron recién tras retry — revisar espera/estado")
    lines.append(footer(path, raw))
    emit(lines, raw, "playwright", path, started)


if __name__ == "__main__":
    main(sys.argv)
